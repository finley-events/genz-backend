from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Profile, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
        )

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "display_name",
            "bio",
            "avatar",
            "country",
            "city",
            "referral_code",
            "badge_level",
            "reputation_score",
        )
        read_only_fields = (
            "referral_code",
            "badge_level",
            "reputation_score",
        )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "role",
            "is_phone_verified",
            "is_kyc_verified",
            "date_joined",
            "profile",
        )
        read_only_fields = fields


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "display_name",
            "bio",
            "avatar",
            "country",
            "city",
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                "The new password must be different from the old password."
            )
        return attrs


def save(self, **kwargs):
    user = self.context["request"].user
    data = self.validated_data

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if old_password is None or new_password is None:
        raise serializers.ValidationError("Missing password fields.")

    if not user.check_password(old_password):
        raise serializers.ValidationError({"old_password": "Incorrect password."})

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return user
