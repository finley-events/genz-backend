from decimal import Decimal

from rest_framework import serializers

from .models import MpesaTransaction


class DepositSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=20,
    )

    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        min_value=Decimal("1"),
    )

    def validate_phone_number(self, value):
        """
        Convert and validate Kenyan phone number.
        """

        value = value.strip()

        if value.startswith("07"):
            value = "254" + value[1:]

        elif value.startswith("+254"):
            value = value[1:]

        if not value.startswith("254"):
            raise serializers.ValidationError("Phone number must start with 254.")

        if len(value) != 12:
            raise serializers.ValidationError("Invalid phone number length.")

        return value


class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=8,
        min_value=Decimal("0.00000001"),
    )

    phone_number = serializers.CharField(
        max_length=20,
    )

    def validate_phone_number(self, value):
        value = value.strip()

        if value.startswith("07"):
            value = "254" + value[1:]

        elif value.startswith("+254"):
            value = value[1:]

        if not value.startswith("254"):
            raise serializers.ValidationError("Phone number must start with 254.")

        if len(value) != 12:
            raise serializers.ValidationError("Invalid phone number.")

        return value


class MpesaTransactionSerializer(serializers.ModelSerializer):
    transaction_reference = serializers.SerializerMethodField()

    class Meta:
        model = MpesaTransaction

        fields = [
            "id",
            "reference",
            "external_reference",
            "checkout_request_id",
            "phone_number",
            "amount_kes",
            "coin_amount",
            "transaction_type",
            "status",
            "transaction_reference",
            "failure_reason",
            "created_at",
            "completed_at",
        ]

        read_only_fields = fields

    def get_transaction_reference(self, obj):
        if obj.transaction:
            return obj.transaction.reference

        return None
