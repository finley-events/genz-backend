import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class UserRole(models.TextChoices):
    USER = "user", _("User")
    SPONSOR = "sponsor", _("Sponsor")
    MODERATOR = "moderator", _("Moderator")
    ADMIN = "admin", _("Admin")


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    username = models.CharField(
        max_length=50,
        unique=True,
    )

    email = models.EmailField(
        unique=True,
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
    )

    first_name = models.CharField(
        max_length=100,
        blank=True,
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    is_phone_verified = models.BooleanField(default=False)
    is_kyc_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects: UserManager = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username",
        "phone_number",
    ]

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    display_name = models.CharField(
        max_length=100,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    country = models.CharField(
        max_length=100,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    referral_code = models.CharField(
        max_length=32,
        unique=True,
    )

    badge_level = models.PositiveIntegerField(
        default=1,
    )

    reputation_score = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "profiles"

    def __str__(self):
        return f"{self.user.username} Profile"
