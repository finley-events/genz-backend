# apps/wallets/models.py

import uuid

from django.conf import settings
from django.db import models
from decimal import Decimal


class Wallet(models.Model):
    """
    Represents a user's Gen Z Coin wallet.
    The ledger is the source of truth for balances.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    wallet_address = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.wallet_address}"


class WalletBalance(models.Model):
    """
    Cached wallet balance.

    This is NOT the source of truth.
    Actual balances should be derived from
    ledger entries in the transactions app.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    wallet = models.OneToOneField(
        Wallet,
        on_delete=models.CASCADE,
        related_name="balance",
    )

    available_balance = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )

    locked_balance = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Wallet Balance"
        verbose_name_plural = "Wallet Balances"

    def __str__(self):
        return (
            f"{self.wallet.wallet_address} | "
            f"Available: {self.available_balance} Z | "
            f"Locked: {self.locked_balance} Z"
        )
