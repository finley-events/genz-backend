from rest_framework import serializers


class OTPSerializer(serializers.Serializer):

    account_id = serializers.CharField(max_length=50)
