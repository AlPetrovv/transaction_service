from decimal import Decimal

from django.db import models

from .exceptions import SystemWalletDoesNotExist


class Wallet(models.Model):
    balance = models.DecimalField(
        'Balance',
        max_digits=19,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=Decimal('0.00')),
                name='wallet_balance_non_negative',
            ),
        ]

    def __str__(self) -> str:
        return f'Wallet {self.pk}'


class SystemWallet(models.Model):
    """Pointer to the wallet that receives commission. There must be exactly one row."""

    wallet = models.OneToOneField(
        Wallet,
        on_delete=models.PROTECT,
        related_name='system_marker',
    )

    def save(self, *args, **kwargs):
        # Guard against creating a second row. The signal that bootstraps
        # this model serializes on the database, so this is mostly a safety net.
        if not self.pk and SystemWallet.objects.exists():
            raise ValueError("SystemWallet already exists")
        super().save(*args, **kwargs)

    @classmethod
    def get_wallet_id(cls) -> int:
        wallet_id = cls.objects.values_list('wallet_id', flat=True).first()
        if wallet_id is None:
            raise SystemWalletDoesNotExist()
        return wallet_id


class Transaction(models.Model):
    amount = models.DecimalField(
        'Amount',
        max_digits=19,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    from_wallet = models.ForeignKey(
        Wallet,
        related_name='out_transactions',
        on_delete=models.PROTECT,
    )
    to_wallet = models.ForeignKey(
        Wallet,
        related_name='in_transactions',
        on_delete=models.PROTECT,
    )
    commission_tx = models.OneToOneField(
        'self',
        on_delete=models.PROTECT,
        related_name='parent_transaction',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['from_wallet', '-created_at']),
            models.Index(fields=['to_wallet', '-created_at']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                name='transaction_amount_positive',
                condition=models.Q(amount__gte=Decimal('0.01')),
            ),
            models.CheckConstraint(
                name='transaction_from_neq_to',
                condition=~models.Q(from_wallet=models.F('to_wallet')),
            ),
        ]

    def __str__(self) -> str:
        return f'Transaction(id={self.pk})'
