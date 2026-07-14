from uuid import uuid4

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model with timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DerivOAuthSession(TimeStampedModel):
    """
    Temporary OAuth session used during PKCE authentication.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )

    state = models.CharField(
        max_length=255,
        unique=True,
    )

    code_verifier = models.TextField()

    expires_at = models.DateTimeField()

    used = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "deriv_oauth_sessions"
        ordering = ["-created_at"]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return self.state


class DerivAccount(TimeStampedModel):
    """
    Connected Deriv trading account.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )

    login_id = models.CharField(
        max_length=50,
        unique=True,
    )

    deriv_user_id = models.CharField(
        max_length=100,
        db_index=True,
    )

    email = models.EmailField(
        blank=True,
    )

    currency = models.CharField(
        max_length=10,
    )

    country = models.CharField(
        max_length=100,
        blank=True,
    )

    landing_company = models.CharField(
        max_length=100,
        blank=True,
    )

    is_virtual = models.BooleanField(
        default=False,
    )

    is_connected = models.BooleanField(
        default=True,
    )

    access_token = models.TextField()

    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_synced = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "deriv_accounts"
        ordering = ["-created_at"]

    def __str__(self):
        return self.login_id


class TradingSession(TimeStampedModel):
    """
    Tracks active user sessions on the trading platform.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )

    deriv_account = models.ForeignKey(
        DerivAccount,
        on_delete=models.CASCADE,
        related_name="sessions",
    )

    session_id = models.CharField(
        max_length=255,
        unique=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    connected_at = models.DateTimeField(
        auto_now_add=True,
    )

    disconnected_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_activity = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "deriv_trading_sessions"
        ordering = ["-connected_at"]

    def __str__(self):
        return f"{self.deriv_account.login_id} ({self.session_id})"
