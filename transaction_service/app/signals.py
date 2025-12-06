from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Wallet, SystemWallet


@receiver(post_migrate)
def create_system_wallet(sender, **kwargs):
    if sender.label != "app":
        return

    if not SystemWallet.objects.exists():
        wallet = Wallet.objects.create(balance=0)
        SystemWallet.objects.create(wallet=wallet)
