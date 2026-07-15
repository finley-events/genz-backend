from rest_framework import serializers

from apps.deriv.models import DerivTradingAccount


class DerivTradingAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DerivTradingAccount
        fields = (
            "account_id",
            "account_type",
            "currency",
            "balance",
            "group",
            "status",
        )
