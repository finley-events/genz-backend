# apps/wallets/serializers.py

from rest_framework import serializers

from .models import Wallet, WalletBalance


class WalletBalanceSerializer(serializers.ModelSerializer):
    """
    Serializer for cached wallet balances.
    """

    class Meta:
        model = WalletBalance
        fields = (
            "available_balance",
            "locked_balance",
            "updated_at",
        )
        read_only_fields = fields


class WalletSerializer(serializers.ModelSerializer):
    """
    Basic wallet serializer.
    """

    class Meta:
        model = Wallet
        fields = (
            "id",
            "wallet_address",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class WalletDetailSerializer(serializers.ModelSerializer):
    """
    Detailed wallet serializer including the cached balance.
    """

    balance = WalletBalanceSerializer(read_only=True)

    class Meta:
        model = Wallet
        fields = (
            "id",
            "wallet_address",
            "is_active",
            "balance",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class WalletAddressSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for exposing only the wallet address.
    """

    class Meta:
        model = Wallet
        fields = ("wallet_address",)
        read_only_fields = fields
