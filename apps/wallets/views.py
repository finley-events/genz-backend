# apps/wallets/views.py

from typing import cast

from rest_framework import generics, permissions
from rest_framework.request import Request

from apps.users.models import User

from .models import Wallet
from .serializers import (
    WalletAddressSerializer,
    WalletBalanceSerializer,
    WalletDetailSerializer,
)
from .services import WalletService


class WalletDetailView(generics.RetrieveAPIView):
    """
    Retrieve the authenticated user's wallet details.
    """

    serializer_class = WalletDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Wallet:
        request = cast(Request, self.request)
        user = cast(User, request.user)
        return Wallet.objects.get(user=user)


class WalletBalanceView(generics.RetrieveAPIView):
    """
    Retrieve the authenticated user's cached wallet balance.
    """

    serializer_class = WalletBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        request = cast(Request, self.request)
        user = cast(User, request.user)
        return Wallet.objects.get(user=user)

        return WalletService.get_balance(user.wallet)


class WalletAddressView(generics.RetrieveAPIView):
    """
    Retrieve only the authenticated user's wallet address.
    """

    serializer_class = WalletAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Wallet:
        request = cast(Request, self.request)
        user = cast(User, request.user)
        return Wallet.objects.get(user=user)
