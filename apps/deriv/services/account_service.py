from typing import Any, cast

import requests

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.deriv.models import DerivAccount


class DerivAccountService:
    """
    Handles authenticated account-related requests to Deriv.
    """

    def __init__(self, access_token: str):
        self.access_token = access_token

        self.base_url = settings.DERIV_API_BASE.rstrip("/")

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Deriv-App-ID": settings.DERIV_CLIENT_ID,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    # ----------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------

    def _get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """
        Internal GET request helper.
        """

        response = requests.get(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            headers=self.headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def _post(
        self,
        endpoint: str,
        payload: dict | None = None,
    ) -> dict[str, Any]:
        """
        Internal POST request helper.
        """

        response = requests.post(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            headers=self.headers,
            json=payload or {},
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    # ----------------------------------------------------
    # ACCOUNT
    # ----------------------------------------------------

    def get_accounts(self) -> dict[str, Any]:
        """
        Get all trading accounts.
        """

        return self._get("/trading/v1/options/accounts")

    def get_primary_account(self) -> dict[str, Any]:
        """
        Returns the primary trading account.
        Adjust this method if Deriv changes their response.
        """

        accounts = self.get_accounts()

        if isinstance(accounts, list):
            return cast(list[dict[str, Any]], accounts)[0]

        if "accounts" in accounts:
            return accounts["accounts"][0]

        return accounts

    def get_profile(self) -> dict[str, Any]:
        """
        Get trader profile.
        """

        return self._get("/trading/v1/profile")

    def create_account(
        self,
        currency: str,
        group: str,
        account_type: str,
    ) -> dict[str, Any]:
        """
        Create a trading account.
        """

        payload = {
            "currency": currency,
            "group": group,
            "account_type": account_type,
        }

        return self._post(
            "/trading/v1/options/accounts",
            payload,
        )

    def get_balance(self) -> dict[str, Any]:
        """
        Get account balance.
        """

        return self._get("/trading/v1/balance")

    def get_settings(self) -> dict[str, Any]:
        """
        Get account settings.
        """

        return self._get("/trading/v1/settings")

    def get_limits(self) -> dict[str, Any]:
        """
        Get trading limits.
        """

        return self._get("/trading/v1/limits")

    def get_currencies(self) -> dict[str, Any]:
        """
        Get supported currencies.
        """

        return self._get("/trading/v1/currencies")

    def ping(self) -> dict[str, Any]:
        """
        Verify that the access token is still valid.
        """

        return self.get_profile()

    # ----------------------------------------------------
    # DATABASE
    # ----------------------------------------------------

    @transaction.atomic
    def save_account(
        self,
        account_data: dict[str, Any],
        access_token: str,
        expires_in: int,
    ) -> DerivAccount:
        """
        Create or update a connected Deriv account.
        """

        expires_at = timezone.now() + timezone.timedelta(
            seconds=expires_in,
        )

        account, _ = DerivAccount.objects.update_or_create(
            login_id=account_data["loginid"],
            defaults={
                "deriv_user_id": account_data["user_id"],
                "email": account_data.get("email", ""),
                "currency": account_data["currency"],
                "country": account_data.get("country", ""),
                "landing_company": account_data.get(
                    "landing_company",
                    "",
                ),
                "is_virtual": account_data.get(
                    "is_virtual",
                    False,
                ),
                "is_connected": True,
                "access_token": access_token,
                "token_expires_at": expires_at,
                "last_synced": timezone.now(),
            },
        )

        return account

    # ----------------------------------------------------
    # FUTURE METHODS
    # ----------------------------------------------------

    def refresh(self):
        """
        Reserved for future token refresh support.
        """

        raise NotImplementedError

    def revoke(self):
        """
        Reserved for logout / token revocation.
        """

        raise NotImplementedError
