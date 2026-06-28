# apps/transactions/models.py

import uuid

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    # transactions/models.py

    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        TRANSFER = "transfer", "Transfer"
        REWARD = "reward", "Reward"
        MARKET_PAYOUT = "market_payout", "Market Payout"
        CAMPAIGN_FUNDING = "campaign_funding", "Campaign Funding"
        CAMPAIGN_REWARD = "campaign_reward", "Campaign Reward"
        REFUND = "refund", "Refund"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REVERSED = "reversed", "Reversed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    reference = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )

    transaction_type = models.CharField(
        max_length=32,
        choices=TransactionType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
    )

    currency = models.CharField(
        max_length=10,
        default="Z",
    )

    description = models.TextField(
        blank=True,
    )

    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiated_transactions",
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

    def __str__(self):
        return f"{self.reference} ({self.transaction_type})"


class LedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )

    # Replace with ForeignKey("wallets.Wallet", ...)
    # once the wallets app is implemented.

    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )

    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.transaction.reference} - " f"{self.entry_type} - {self.amount}"
