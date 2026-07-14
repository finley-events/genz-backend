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


class DerivConnection(TimeStampedModel):

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )

    access_token = models.TextField()

    token_type = models.CharField(
        max_length=20,
        default="Bearer",
    )

    scopes = models.CharField(
        max_length=255,
        blank=True,
    )

    token_expires_at = models.DateTimeField()

    is_connected = models.BooleanField(
        default=True,
    )

    connected_at = models.DateTimeField(
        auto_now_add=True,
    )

    disconnected_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_synced = models.DateTimeField(
        null=True,
        blank=True,
    )

    raw_token = models.JSONField(
        default=dict,
        blank=True,
    )



class DerivTradingAccount(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )

    connection = models.ForeignKey(
        DerivConnection,
        related_name="accounts",
        on_delete=models.CASCADE,
    )

    account_id = models.CharField(
        max_length=50,
        unique=True,
    )

    account_type = models.CharField(
        max_length=20,
    )

    currency = models.CharField(
        max_length=10,
    )

    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
    )

    group = models.CharField(
        max_length=50,
    )

    status = models.CharField(
        max_length=30,
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
    )
