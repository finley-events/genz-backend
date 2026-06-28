# apps/wallets/admin.py

from django.contrib import admin

from .models import Wallet, WalletBalance


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "wallet_address",
        "user",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "wallet_address",
        "user__username",
        "user__email",
        "user__phone_number",
    )

    readonly_fields = (
        "id",
        "wallet_address",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


@admin.register(WalletBalance)
class WalletBalanceAdmin(admin.ModelAdmin):
    list_display = (
        "wallet",
        "available_balance",
        "locked_balance",
        "updated_at",
    )

    search_fields = (
        "wallet__wallet_address",
        "wallet__user__username",
        "wallet__user__email",
    )

    readonly_fields = (
        "id",
        "updated_at",
    )

    ordering = ("-updated_at",)
