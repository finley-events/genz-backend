# apps/transactions/views.py

from typing import cast

from rest_framework import generics, permissions

from apps.users.models import User

from .models import Transaction
from .serializers import (
    TransactionDetailSerializer,
    TransactionSerializer,
)


class TransactionListView(generics.ListAPIView):
    """
    List transactions initiated by the authenticated user.
    """

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = cast(User, self.request.user)

        return Transaction.objects.filter(
            initiated_by=user,
        ).order_by("-created_at")


class TransactionDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single transaction belonging to the
    authenticated user.
    """

    serializer_class = TransactionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = cast(User, self.request.user)

        return Transaction.objects.filter(
            initiated_by=user,
        )


class WalletStatementView(generics.ListAPIView):
    """
    Return the authenticated user's transaction history.
    This can later be extended with date filters,
    exports, or pagination.
    """

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = cast(User, self.request.user)

        return Transaction.objects.filter(
            initiated_by=user,
        ).order_by("-created_at")
