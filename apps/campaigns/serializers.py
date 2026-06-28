from rest_framework import serializers

from .models import (
    Campaign,
    CampaignTask,
    CampaignParticipation,
    CampaignSubmission,
    CampaignReward,
    CampaignFunding,
)


class CampaignSerializer(serializers.ModelSerializer):

    sponsor_username = serializers.CharField(
        source="sponsor.username",
        read_only=True,
    )

    class Meta:
        model = Campaign

        fields = [
            "id",
            "sponsor",
            "sponsor_username",
            "title",
            "slug",
            "description",
            "campaign_type",
            "status",
            "budget",
            "remaining_budget",
            "reward_per_action",
            "start_date",
            "end_date",
            "visibility",
            "max_participants",
            "current_participants",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "budget",
            "remaining_budget",
            "current_participants",
            "created_at",
            "updated_at",
        ]


class CampaignTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTask

        fields = [
            "id",
            "campaign",
            "title",
            "description",
            "task_type",
            "reward",
            "verification_type",
            "max_completions",
        ]

        read_only_fields = [
            "id",
        ]


class CampaignParticipationSerializer(serializers.ModelSerializer):
    campaign_title = serializers.CharField(
        source="campaign.title",
        read_only=True,
    )

    class Meta:
        model = CampaignParticipation

        fields = [
            "id",
            "campaign",
            "campaign_title",
            "user",
            "status",
            "reward_paid",
            "reward_amount",
            "joined_at",
            "completed_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "status",
            "reward_paid",
            "reward_amount",
            "joined_at",
            "completed_at",
        ]


class CampaignSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignSubmission

        fields = [
            "id",
            "participation",
            "task",
            "proof_url",
            "proof_image",
            "notes",
            "status",
            "verified_by",
            "verified_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "verified_by",
            "verified_at",
            "created_at",
        ]


class CampaignRewardSerializer(serializers.ModelSerializer):
    transaction_reference = serializers.SerializerMethodField()

    def get_transaction_reference(
        self,
        obj,
    ):
        if obj.transaction:
            return obj.transaction.reference

        return None

    class Meta:
        model = CampaignReward

        fields = [
            "id",
            "participation",
            "transaction",
            "transaction_reference",
            "wallet",
            "amount",
            "status",
            "paid_at",
        ]

        read_only_fields = [
            "id",
            "transaction",
            "transaction_reference",
            "wallet",
            "amount",
            "status",
            "paid_at",
        ]


class CampaignFundingSerializer(serializers.ModelSerializer):
    transaction_reference = serializers.SerializerMethodField()

    def get_transaction_reference(
        self,
        obj,
    ):
        if obj.transaction:
            return obj.transaction.reference

        return None

    class Meta:
        model = CampaignFunding

        fields = [
            "id",
            "campaign",
            "sponsor",
            "wallet",
            "transaction",
            "transaction_reference",
            "funding_type",
            "amount",
            "status",
            "notes",
            "completed_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "transaction",
            "transaction_reference",
            "status",
            "completed_at",
            "created_at",
        ]


class JoinCampaignSerializer(serializers.Serializer):
    campaign_id = serializers.UUIDField()


class SubmitTaskSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()

    proof_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )

    proof_image = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class VerifySubmissionSerializer(serializers.Serializer):
    submission_id = serializers.UUIDField()


class RejectSubmissionSerializer(serializers.Serializer):
    submission_id = serializers.UUIDField()


class FundCampaignSerializer(serializers.Serializer):
    campaign_id = serializers.UUIDField()

    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=8,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class RewardPayoutSerializer(serializers.Serializer):
    participation_id = serializers.UUIDField()


class CreateCampaignSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)

    description = serializers.CharField()

    campaign_type = serializers.CharField()

    reward_per_action = serializers.DecimalField(
        max_digits=20,
        decimal_places=8,
    )

    start_date = serializers.DateTimeField()

    end_date = serializers.DateTimeField()

    visibility = serializers.CharField()

    max_participants = serializers.IntegerField()
