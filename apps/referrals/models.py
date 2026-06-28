# apps/referrals/models.py

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class Referral(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUALIFIED = "qualified", "Qualified"
        REWARDED = "rewarded", "Rewarded"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="referrals_made",
    )

    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="referral",
    )

    referral_code_used = models.CharField(
        max_length=64,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    reward_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    qualified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rewarded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["referral_code_used"]),
        ]

    def __str__(self):
        return (
            f"{self.referrer.username} → "
            f"{self.referred_user.username} "
            f"({self.status})"
        )


class ReferralReward(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    referral = models.OneToOneField(
        Referral,
        on_delete=models.CASCADE,
        related_name="reward",
    )

    transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.PROTECT,
        related_name="referral_reward",
        null=True,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Referral Reward " f"{self.amount} Z " f"({self.status})"
