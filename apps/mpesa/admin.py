from django.contrib import admin

from .models import (
    MpesaTransaction,
    MpesaWebhookLog,
)


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "user",
        "transaction_type",
        "amount_kes",
        "coin_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "transaction_type",
        "created_at",
    )

    search_fields = (
        "reference",
        "external_reference",
        "checkout_request_id",
        "phone_number",
        "user__email",
        "user__username",
    )

    readonly_fields = (
        "id",
        "reference",
        "external_reference",
        "checkout_request_id",
        "transaction",
        "raw_request",
        "raw_response",
        "raw_callback",
        "created_at",
        "updated_at",
        "completed_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "user",
                    "reference",
                    "external_reference",
                    "checkout_request_id",
                    "transaction",
                )
            },
        ),
        (
            "Payment Details",
            {
                "fields": (
                    "transaction_type",
                    "phone_number",
                    "amount_kes",
                    "coin_amount",
                    "status",
                    "failure_reason",
                )
            },
        ),
        (
            "Audit Trail",
            {
                "fields": (
                    "raw_request",
                    "raw_response",
                    "raw_callback",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "completed_at",
                )
            },
        ),
    )


@admin.register(MpesaWebhookLog)
class MpesaWebhookLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mpesa_transaction",
        "processed",
        "created_at",
    )

    list_filter = (
        "processed",
        "created_at",
    )

    search_fields = (
        "mpesa_transaction__reference",
        "mpesa_transaction__external_reference",
    )

    readonly_fields = (
        "id",
        "mpesa_transaction",
        "payload",
        "processed",
        "processing_error",
        "created_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Webhook",
            {
                "fields": (
                    "id",
                    "mpesa_transaction",
                    "processed",
                    "processing_error",
                )
            },
        ),
        (
            "Payload",
            {
                "fields": ("payload",),
            },
        ),
        (
            "Timestamp",
            {"fields": ("created_at",)},
        ),
    )
