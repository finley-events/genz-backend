# users/validators.py

import re

from django.core.exceptions import ValidationError

USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]{3,30}$")
PHONE_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")
REFERRAL_CODE_REGEX = re.compile(r"^[A-Z0-9]{6,32}$")


def validate_username(value: str) -> str:
    """
    Valid usernames:
    - 3 to 30 characters
    - Letters
    - Numbers
    - Underscores
    """

    value = value.strip()

    if not USERNAME_REGEX.fullmatch(value):
        raise ValidationError(
            "Username must be 3-30 characters long and contain only "
            "letters, numbers, and underscores."
        )

    return value


def validate_phone_number(value: str) -> str:
    """
    Validate phone numbers in E.164 format.

    Example:
        +254712345678
        +14155552671
    """

    value = value.strip().replace(" ", "")

    if not PHONE_REGEX.fullmatch(value):
        raise ValidationError(
            "Phone number must be in international E.164 format "
            "(e.g. +254712345678)."
        )

    return value


def validate_display_name(value: str) -> str:
    """
    Basic validation for profile display names.
    """

    value = value.strip()

    if len(value) > 100:
        raise ValidationError("Display name cannot exceed 100 characters.")

    return value


def validate_referral_code(value: str) -> str:
    """
    Referral codes should be uppercase alphanumeric strings.
    """

    value = value.strip().upper()

    if not REFERRAL_CODE_REGEX.fullmatch(value):
        raise ValidationError("Referral code format is invalid.")

    return value
