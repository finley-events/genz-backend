# apps/campaigns/models.py

from django.utils import timezone
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Campaign(models.Model):
    class CampaignType(models.TextChoices):
        SHARE = "share", "Share"
        CLICK = "click", "Click"
        DOWNLOAD = "download", "Download"
        SIGNUP = "signup", "Sign Up"
        SURVEY = "survey", "Survey"
        VIDEO = "video", "Video"
        CUSTOM = "custom", "Custom"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_REVIEW = "pending_review", "Pending Review"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        INVITE_ONLY = "invite_only", "Invite Only"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    sponsor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="campaigns",
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        max_length=300,
    )

    description = models.TextField()

    campaign_type = models.CharField(
        max_length=20,
        choices=CampaignType.choices,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )

    budget = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )

    remaining_budget = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )

    reward_per_action = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )

    currency = models.CharField(
        max_length=10,
        default="Z",
    )

    max_participants = models.PositiveIntegerField(default=0)

    current_participants = models.PositiveIntegerField(default=0)

    requires_verification = models.BooleanField(default=True)

    start_date = models.DateTimeField()

    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["campaign_type"]),
            models.Index(fields=["visibility"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CampaignMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        FILE = "file", "File"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="media",
    )

    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
    )

    image = models.ImageField(
        upload_to="campaigns/images/",
        blank=True,
        null=True,
    )

    video = models.FileField(
        upload_to="campaigns/videos/",
        blank=True,
        null=True,
    )

    file = models.FileField(
        upload_to="campaigns/files/",
        blank=True,
        null=True,
    )

    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.campaign.title} ({self.media_type})"


class CampaignTask(models.Model):
    class TaskType(models.TextChoices):
        SHARE = "share", "Share"
        VISIT = "visit", "Visit"
        CLICK = "click", "Click"
        WATCH = "watch", "Watch"
        DOWNLOAD = "download", "Download"
        SIGNUP = "signup", "Sign Up"
        REFERRAL = "referral", "Referral"
        MANUAL = "manual", "Manual"

    class VerificationType(models.TextChoices):
        AUTOMATIC = "automatic", "Automatic"
        MANUAL = "manual", "Manual"
        HYBRID = "hybrid", "Hybrid"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
    )

    reward = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )

    verification_type = models.CharField(
        max_length=20,
        choices=VerificationType.choices,
        default=VerificationType.MANUAL,
    )

    max_completions = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class CampaignParticipation(models.Model):
    class Status(models.TextChoices):
        JOINED = "joined", "Joined"
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted", "Submitted"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        REWARDED = "rewarded", "Rewarded"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="participants",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="campaign_participations",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.JOINED,
    )

    reward_paid = models.BooleanField(default=False)

    reward_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ("campaign", "user")

    def __str__(self):
        return f"{self.user} - {self.campaign}"


class CampaignSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    participation = models.ForeignKey(
        CampaignParticipation,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    task = models.ForeignKey(
        CampaignTask,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    proof_url = models.URLField(
        blank=True,
        null=True,
    )

    proof_image = models.ImageField(
        upload_to="campaigns/proofs/",
        blank=True,
        null=True,
    )

    notes = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_campaign_submissions",
    )

    def __str__(self):
        return f"{self.task.title} ({self.status})"


class CampaignReward(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    participation = models.OneToOneField(
        CampaignParticipation,
        on_delete=models.CASCADE,
        related_name="reward",
    )

    transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.PROTECT,
        related_name="campaign_reward",
        null=True,
        blank=True,
    )

    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.PROTECT,
        related_name="campaign_rewards",
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

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.amount} Z"


class CampaignFunding(models.Model):
    """
    Records every funding event for a campaign.

    The source of truth for campaign finances.
    """

    class FundingType(models.TextChoices):
        INITIAL = "initial", "Initial Funding"
        TOP_UP = "top_up", "Top Up"
        REFUND = "refund", "Refund"
        ADJUSTMENT = "adjustment", "Adjustment"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="funding_events",
    )

    sponsor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="campaign_funding",
    )

    transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.PROTECT,
        related_name="campaign_funding",
        null=True,
        blank=True,
    )

    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.PROTECT,
        related_name="campaign_funding",
    )

    funding_type = models.CharField(
        max_length=20,
        choices=FundingType.choices,
        default=FundingType.INITIAL,
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

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def mark_completed(self):
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    def mark_failed(self):
        self.status = self.Status.FAILED
        self.save(update_fields=["status"])

    def __str__(self):
        return f"{self.campaign.title} - " f"{self.amount} Z ({self.funding_type})"
