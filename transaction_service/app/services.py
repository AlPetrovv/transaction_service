
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.db.models import F

from .exceptions import (
    InsufficientFunds,
    SelfTransferNotAllowed,
    WalletNotFound,
)
from .models import SystemWallet, Transaction, Wallet

logger = logging.getLogger(__name__)

COMMISSION_THRESHOLD = Decimal('1000')
COMMISSION_RATE = Decimal('0.10')
MONEY_QUANTUM = Decimal('0.01')


def _lock_wallets(wallet_ids: Iterable[int]) -> dict[int, Wallet]:
    """Lock the given wallets in ascending-id order to avoid deadlocks.

    Postgres acquires row locks in the order rows are visited, so an
    ``ORDER BY id`` on the locking SELECT guarantees a total order across
    concurrent callers and eliminates ABBA deadlocks.
    """
    sorted_ids = sorted(set(wallet_ids))
    locked = (
        Wallet.objects
        .select_for_update()
        .filter(pk__in=sorted_ids)
        .order_by('pk')
    )
    by_id = {wallet.pk: wallet for wallet in locked}
    missing = [wid for wid in sorted_ids if wid not in by_id]
    if missing:
        raise WalletNotFound(f"Wallet(s) not found: {missing}")
    return by_id


@transaction.atomic
def make_transfer(
    from_wallet_id: int,
    to_wallet_id: int,
    amount: Decimal,
) -> Transaction:
    """Move ``amount`` from one wallet to another.

    For amounts >= ``COMMISSION_THRESHOLD``, ``COMMISSION_RATE`` is deducted
    from ``amount`` and routed to the system wallet; the recipient receives
    the remainder. The sender's total debit always equals ``amount``.
    """
    if from_wallet_id == to_wallet_id:
        raise SelfTransferNotAllowed()

    apply_commission = amount >= COMMISSION_THRESHOLD
    commission_amount = Decimal('0.00')
    system_wallet_id: int | None = None

    if apply_commission:
        system_wallet_id = SystemWallet.get_wallet_id()
        # System wallet sending money to itself would violate the
        # from != to constraint; skip commission in that pathological case.
        if from_wallet_id != system_wallet_id:
            commission_amount = (amount * COMMISSION_RATE).quantize(MONEY_QUANTUM)
        else:
            apply_commission = False
            system_wallet_id = None

    main_amount = amount - commission_amount

    wallet_ids = {from_wallet_id, to_wallet_id}
    if system_wallet_id is not None:
        wallet_ids.add(system_wallet_id)
    wallets = _lock_wallets(wallet_ids)

    from_wallet = wallets[from_wallet_id]
    if from_wallet.balance < amount:
        raise InsufficientFunds()

    commission_tx: Transaction | None = None
    if apply_commission and system_wallet_id is not None:
        Wallet.objects.filter(pk=system_wallet_id).update(
            balance=F('balance') + commission_amount,
        )
        commission_tx = Transaction.objects.create(
            from_wallet_id=from_wallet_id,
            to_wallet_id=system_wallet_id,
            amount=commission_amount,
        )

    Wallet.objects.filter(pk=from_wallet_id).update(balance=F('balance') - amount)
    Wallet.objects.filter(pk=to_wallet_id).update(balance=F('balance') + main_amount)

    tx = Transaction.objects.create(
        from_wallet_id=from_wallet_id,
        to_wallet_id=to_wallet_id,
        amount=main_amount,
        commission_tx=commission_tx,
    )

    _schedule_notification(tx.pk)
    return tx


def _schedule_notification(transaction_id: int) -> None:

    from .tasks import send_notification

    transaction.on_commit(lambda: send_notification.delay(transaction_id))
