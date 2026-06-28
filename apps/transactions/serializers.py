# apps/transactions/serializers.py

from rest_framework import serializers

from .models import LedgerEntry, Transaction


class LedgerEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for individual ledger entries.
    """

    class Meta:
        model = LedgerEntry
        fields = (
            "id",
            "wallet",
            "entry_type",
            "amount",
            "created_at",
        )
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    """
    Basic serializer for transaction listings.
    """

    class Meta:
        model = Transaction
        fields = (
            "id",
            "reference",
            "transaction_type",
            "status",
            "amount",
            "currency",
            "description",
            "created_at",
            "completed_at",
        )
        read_only_fields = fields


class TransactionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer including ledger entries.
    """

    ledger_entries = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "reference",
            "transaction_type",
            "status",
            "amount",
            "currency",
            "description",
            "initiated_by",
            "created_at",
            "completed_at",
            "ledger_entries",
        )
        read_only_fields = fields

    def get_ledger_entries(self, obj):
        entries = LedgerEntry.objects.filter(transaction=obj).order_by("created_at")

        return LedgerEntrySerializer(
            entries,
            many=True,
        ).data
