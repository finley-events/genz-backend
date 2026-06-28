# apps/transactions/urls.py

from django.urls import path

from .views import (
    TransactionDetailView,
    TransactionListView,
    WalletStatementView,
)

app_name = "transactions"

urlpatterns = [
    # List all transactions for the authenticated user
    path(
        "",
        TransactionListView.as_view(),
        name="transaction-list",
    ),
    # Retrieve a specific transaction
    path(
        "<uuid:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    # Wallet statement / transaction history
    path(
        "statement/",
        WalletStatementView.as_view(),
        name="wallet-statement",
    ),
]
