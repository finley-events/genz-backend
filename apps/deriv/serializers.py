from rest_framework import serializers

from .models import DerivAccount


class AuthorizeSerializer(serializers.Serializer):
    """
    Validate Deriv authorization token.
    """

    token = serializers.CharField(
        max_length=500,
        trim_whitespace=True,
    )


class TickSerializer(serializers.Serializer):
    """
    Validate tick request.
    """

    symbol = serializers.CharField(
        max_length=50,
    )


class CandleSerializer(serializers.Serializer):
    """
    Validate candle history request.
    """

    symbol = serializers.CharField(
        max_length=50,
    )

    granularity = serializers.IntegerField(
        default=60,
        min_value=60,
    )

    count = serializers.IntegerField(
        default=100,
        min_value=1,
        max_value=5000,
    )


class ProposalSerializer(serializers.Serializer):
    """
    Validate proposal request.
    """

    symbol = serializers.CharField(max_length=50)

    contract_type = serializers.CharField(max_length=20)

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    basis = serializers.ChoiceField(
        choices=[
            "stake",
            "payout",
        ],
        default="stake",
    )

    currency = serializers.CharField(
        max_length=10,
    )

    duration = serializers.IntegerField(
        min_value=1,
    )

    duration_unit = serializers.ChoiceField(
        choices=[
            "t",
            "s",
            "m",
            "h",
            "d",
        ]
    )


class BuySerializer(serializers.Serializer):
    """
    Validate buy contract request.
    """

    proposal_id = serializers.CharField()

    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


class SellSerializer(serializers.Serializer):
    """
    Validate sell contract request.
    """

    contract_id = serializers.IntegerField()

    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )


class HistorySerializer(serializers.Serializer):
    """
    Validate history request.
    """

    count = serializers.IntegerField(
        default=100,
        min_value=1,
        max_value=5000,
    )


class DerivAccountSerializer(serializers.ModelSerializer):
    """
    Serialize connected Deriv account.
    """

    class Meta:
        model = DerivAccount
        fields = [
            "id",
            "login_id",
            "deriv_user_id",
            "email",
            "currency",
            "country",
            "landing_company",
            "is_virtual",
            "is_connected",
            "last_synced",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class DisconnectSerializer(serializers.Serializer):
    """
    Disconnect account.
    """

    confirm = serializers.BooleanField()
