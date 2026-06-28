# users/services.py

from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Profile, User


class UserService:
    """
    Business logic for user management.
    """

    @staticmethod
    @transaction.atomic
    def register_user(**validated_data: Any) -> User:
        """
        Register a new user.

        Expects:
            username
            email
            phone_number
            password
            first_name (optional)
            last_name (optional)
        """

        password = validated_data.pop("password")
        validate_password(password)

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        # Profile creation is handled by signals.py

        return user

    @staticmethod
    @transaction.atomic
    def update_profile(
        user: User,
        **profile_data: Any,
    ) -> Profile:
        """
        Update editable profile fields.
        """

        profile, _ = Profile.objects.get_or_create(user=user)

        editable_fields = {
            "display_name",
            "bio",
            "avatar",
            "country",
            "city",
        }

        for field, value in profile_data.items():
            if field in editable_fields:
                setattr(profile, field, value)

        profile.save()

        return profile

    @staticmethod
    @transaction.atomic
    def change_password(
        user: User,
        old_password: str,
        new_password: str,
    ) -> None:
        """
        Change a user's password after verifying the old one.
        """

        if not user.check_password(old_password):
            raise ValidationError("Old password is incorrect.")

        validate_password(new_password, user=user)

        user.set_password(new_password)
        user.save(update_fields=["password"])

    @staticmethod
    def get_profile(user: User) -> Profile:
        """
        Return the user's profile.
        """
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    def mark_phone_verified(user: User) -> User:
        """
        Mark a user's phone number as verified.
        """

        if not user.is_phone_verified:
            user.is_phone_verified = True
            user.save(update_fields=["is_phone_verified"])

        return user

    @staticmethod
    def mark_kyc_verified(user: User) -> User:
        """
        Mark a user's KYC status as verified.
        This should normally be called by the KYC app.
        """

        if not user.is_kyc_verified:
            user.is_kyc_verified = True
            user.save(update_fields=["is_kyc_verified"])

        return user
