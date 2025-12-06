from decimal import Decimal

from django.db import transaction
from django.db.models import F

from .exceptions import TransferError
from .models import Wallet, Transaction

COMMISSION = Decimal('0.1')

@transaction.atomic
def make_transfer(from_wallet_id: int, to_wallet_id: int, amount: Decimal) -> Transaction:
    """Make transfer.

    If amount < 1000, transfer without commission
    Else Take 10 % from amount
    """
    if amount < Decimal('1000'):
        tx = transfer(from_wallet_id=from_wallet_id, to_wallet_id=to_wallet_id, amount=amount)
        return tx

    commission_amount = amount * COMMISSION
    system_wallet_id = Wallet.get_system_wallet().id
    commission_tx = transfer(from_wallet_id=from_wallet_id, to_wallet_id=system_wallet_id, amount=commission_amount)
    amount -= commission_amount
    tx = transfer(from_wallet_id=from_wallet_id, to_wallet_id=to_wallet_id, amount=amount, commission_tx=commission_tx)
    return tx


def transfer(from_wallet_id: int, to_wallet_id: int, amount: Decimal, commission_tx: Transaction = None) -> Transaction:
    """Transfer from one wallet to another"""
    try:
        from_wallet = Wallet.objects.select_for_update().get(id=from_wallet_id)
    except Wallet.DoesNotExist:
        raise TransferError("From Wallet does not exist")
    try:
        to_wallet = Wallet.objects.select_for_update().get(id=to_wallet_id)
    except Wallet.DoesNotExist:
        raise TransferError("To Wallet does not exist")

    if from_wallet.balance < amount:
        raise TransferError("Not enough balance")

    Wallet.objects.filter(id=from_wallet.id).update(balance=F('balance') - amount)
    Wallet.objects.filter(id=to_wallet.id).update(balance=F('balance') + amount)

    tx = Transaction.objects.create(
        from_wallet_id=from_wallet_id,
        to_wallet_id=to_wallet_id,
        commission_tx=commission_tx,
        amount=amount,
    )
    return tx