# apps/referrals/serializers.py

from rest_framework import serializers

from .models import Referral, ReferralReward


class ApplyReferralSerializer(serializers.Serializer):
    """
    Serializer for applying a referral code.
    """

    referral_code = serializers.CharField(
        max_length=64,
        trim_whitespace=True,
    )


class ReferralSerializer(serializers.ModelSerializer):
    """
    Basic referral serializer.
    """

    referrer_username = serializers.CharField(
        source="referrer.username",
        read_only=True,
    )

    referred_username = serializers.CharField(
        source="referred_user.username",
        read_only=True,
    )

    class Meta:
        model = Referral
        fields = (
            "id",
            "referrer_username",
            "referred_username",
            "referral_code_used",
            "status",
            "reward_amount",
            "created_at",
            "qualified_at",
            "rewarded_at",
        )
        read_only_fields = fields


class ReferralDetailSerializer(serializers.ModelSerializer):
    """
    Detailed referral serializer.
    """

    referrer_username = serializers.CharField(
        source="referrer.username",
        read_only=True,
    )

    referrer_email = serializers.CharField(
        source="referrer.email",
        read_only=True,
    )

    referred_username = serializers.CharField(
        source="referred_user.username",
        read_only=True,
    )

    referred_email = serializers.CharField(
        source="referred_user.email",
        read_only=True,
    )

    class Meta:
        model = Referral
        fields = (
            "id",
            "referrer_username",
            "referrer_email",
            "referred_username",
            "referred_email",
            "referral_code_used",
            "status",
            "reward_amount",
            "created_at",
            "qualified_at",
            "rewarded_at",
        )
        read_only_fields = fields


class ReferralRewardSerializer(serializers.ModelSerializer):
    """
    Serializer for referral reward records.
    """

    referral_id = serializers.UUIDField(
        source="referral.id",
        read_only=True,
    )

    transaction_reference = serializers.CharField(
        source="transaction.reference",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ReferralReward
        fields = (
            "id",
            "referral_id",
            "transaction_reference",
            "amount",
            "status",
            "created_at",
        )
        read_only_fields = fields
