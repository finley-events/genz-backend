from rest_framework import serializers

from apps.deriv.models import DerivConnection


class DerivConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DerivConnection
        fields = (
            "id",
            "is_connected",
            "token_expires_at",
            "last_synced",
            "created_at",
            "updated_at",
        )
