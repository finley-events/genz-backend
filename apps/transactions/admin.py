# apps/transactions/admin.py

from django.contrib import admin

from .models import LedgerEntry, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "transaction_type",
        "status",
        "amount",
        "currency",
        "initiated_by",
        "created_at",
        "completed_at",
    )

    list_filter = (
        "transaction_type",
        "status",
        "currency",
        "created_at",
    )

    search_fields = (
        "reference",
        "description",
        "initiated_by__username",
        "initiated_by__email",
        "initiated_by__phone_number",
    )

    readonly_fields = (
        "id",
        "reference",
        "created_at",
        "updated_at",
        "completed_at",
    )

    ordering = ("-created_at",)


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        "transaction",
        "wallet",
        "entry_type",
        "amount",
        "created_at",
    )

    list_filter = (
        "entry_type",
        "created_at",
    )

    search_fields = (
        "transaction__reference",
        "wallet__wallet_address",
        "wallet__user__username",
        "wallet__user__email",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = ("-created_at",)
