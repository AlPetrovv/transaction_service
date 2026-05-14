from django.contrib import admin

from .models import SystemWallet, Transaction, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('id',)


@admin.register(SystemWallet)
class SystemWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_wallet_id', 'to_wallet_id', 'amount', 'commission_tx_id', 'created_at')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
    list_select_related = ('from_wallet', 'to_wallet', 'commission_tx')
