# apps/wallets/urls.py

from django.urls import path

from .views import (
    WalletAddressView,
    WalletBalanceView,
    WalletDetailView,
)

app_name = "wallets"

urlpatterns = [
    # Get the authenticated user's wallet details
    path(
        "me/",
        WalletDetailView.as_view(),
        name="wallet-detail",
    ),
    # Get the authenticated user's balance
    path(
        "balance/",
        WalletBalanceView.as_view(),
        name="wallet-balance",
    ),
    # Get only the authenticated user's wallet address
    path(
        "address/",
        WalletAddressView.as_view(),
        name="wallet-address",
    ),
]
