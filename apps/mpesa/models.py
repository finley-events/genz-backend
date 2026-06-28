# apps/mpesa/models.py

import uuid

from django.conf import settings
from django.db import models


class MpesaTransaction(models.Model):
    """
    Stores all PayHero/M-Pesa interactions.

    This model tracks:
    - STK Push deposits
    - B2C withdrawals
    - Callbacks
    - Internal transaction linkage
    """

    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="mpesa_transactions",
    )

    reference = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Internal system reference",
    )

    external_reference = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        db_index=True,
        help_text="Reference sent to PayHero",
    )

    checkout_request_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="PayHero checkout request ID",
    )

    phone_number = models.CharField(
        max_length=20,
    )

    amount_kes = models.DecimalField(
        max_digits=20,
        decimal_places=2,
    )

    coin_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        help_text="Equivalent Gen Z Coin amount",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mpesa_transaction",
    )

    raw_request = models.JSONField(
        default=dict,
        blank=True,
    )

    raw_response = models.JSONField(
        default=dict,
        blank=True,
    )

    raw_callback = models.JSONField(
        default=dict,
        blank=True,
    )

    failure_reason = models.TextField(
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["external_reference"]),
            models.Index(fields=["status"]),
            models.Index(fields=["transaction_type"]),
        ]

    def __str__(self):
        return f"{self.reference} | " f"{self.transaction_type} | " f"{self.status}"


class MpesaWebhookLog(models.Model):
    """
    Stores every webhook exactly as received from PayHero.

    This provides:
    - Audit trail
    - Debugging
    - Replay capability
    - Fraud investigation support
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    mpesa_transaction = models.ForeignKey(
        "mpesa.MpesaTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="webhook_logs",
    )

    payload = models.JSONField()

    processed = models.BooleanField(
        default=False,
    )

    processing_error = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Webhook {self.id} | Processed={self.processed}"
