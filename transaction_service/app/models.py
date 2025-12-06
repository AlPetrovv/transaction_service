from decimal import Decimal

from django.db import models

from .exceptions import SystemWalletDoesNotExist


class Wallet(models.Model):
    balance = models.DecimalField(
        'Balance',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=Decimal('0.00')),
                name='balance_gte_0.00',
            ),
        ]
    def __str__(self):
        return f"Wallet {self.id}"


    @classmethod
    def get_system_wallet(cls) -> 'Wallet':
        try:
            wallet = SystemWallet.objects.get().wallet
        except SystemWallet.DoesNotExist:
            raise SystemWalletDoesNotExist()
        return wallet


class SystemWallet(models.Model):
    wallet = models.OneToOneField("Wallet", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if SystemWallet.objects.exists() and not self.pk:
            raise ValueError("SystemWallet already exists!")
        super().save(*args, **kwargs)


class Transaction(models.Model):
    amount: Decimal = models.DecimalField(
        'Amount',
        max_digits=10,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    from_wallet = models.ForeignKey("Wallet", related_name="out_transactions", on_delete=models.PROTECT)
    to_wallet = models.ForeignKey("Wallet", related_name="inc_transactions", on_delete=models.PROTECT)
    commission_tx = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)


    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['from_wallet', '-created_at']),
            models.Index(fields=['to_wallet', '-created_at']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                name='amount_gte_0.01',
                condition=models.Q(amount__gte=Decimal('0.01')),
            ),
        ]

    def __str__(self):
        return f"Transaction(id={self.id})"