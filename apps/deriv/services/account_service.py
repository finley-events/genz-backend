from typing import Any, cast
import logging

import requests

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.deriv.models import (
    DerivConnection,
    DerivTradingAccount,
)


logger = logging.getLogger(__name__)


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

        logger.info("=" * 80)
        logger.info("DerivAccountService initialized")
        logger.info("Base URL: %s", self.base_url)
        logger.info("Client ID: %s", settings.DERIV_CLIENT_ID)
        logger.info("Authorization header: Bearer ********")
        logger.info("=" * 80)

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

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        logger.info("=" * 80)
        logger.info("DERIV GET REQUEST")
        logger.info("URL: %s", url)
        logger.info("Params: %s", params)
        logger.info(
            "Headers: %s",
            {
                **self.headers,
                "Authorization": "Bearer ********",
            },
        )

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30,
            )

            logger.info("HTTP STATUS: %s", response.status_code)
            logger.info("RESPONSE TEXT: %s", response.text)

            response.raise_for_status()

            data = response.json()

            logger.info("PARSED JSON:")
            logger.info(data)
            logger.info("=" * 80)

            return data

        except Exception:
            logger.exception("GET request failed.")
            raise

    def _post(
        self,
        endpoint: str,
        payload: dict | None = None,
    ) -> dict[str, Any]:
        """
        Internal POST request helper.
        """

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        logger.info("=" * 80)
        logger.info("DERIV POST REQUEST")
        logger.info("URL: %s", url)
        logger.info("Payload: %s", payload)
        logger.info(
            "Headers: %s",
            {
                **self.headers,
                "Authorization": "Bearer ********",
            },
        )

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload or {},
                timeout=30,
            )

            logger.info("HTTP STATUS: %s", response.status_code)
            logger.info("RESPONSE TEXT: %s", response.text)

            response.raise_for_status()

            data = response.json()

            logger.info("PARSED JSON:")
            logger.info(data)
            logger.info("=" * 80)

            return data

        except Exception:
            logger.exception("POST request failed.")
            raise

    # ----------------------------------------------------
    # ACCOUNT
    # ----------------------------------------------------

    def get_accounts(self) -> dict[str, Any]:
        """
        Get all trading accounts.
        """

        logger.info("Fetching Deriv trading accounts...")

        return self._get("/trading/v1/options/accounts")

    def get_trading_accounts(self) -> list[dict[str, Any]]:
        """
        Returns every trading account associated with the OAuth connection.
        """

        response = self.get_accounts()

        return response.get("data", [])

    def get_primary_account(self) -> dict[str, Any]:
        """
        Returns the first trading account.
        """

        logger.info("Selecting primary account...")

        response = self.get_accounts()

        logger.info("Accounts response:")
        logger.info(response)

        if "data" not in response:
            raise ValueError("Deriv response does not contain a 'data' field.")

        accounts = response["data"]

        if not accounts:
            raise ValueError("No trading accounts returned.")

        account = accounts[0]

        logger.info("Primary account:")
        logger.info(account)

        return account

    def get_profile(self) -> dict[str, Any]:
        """
        Get trader profile.
        """

        logger.info("Fetching profile...")

        return self._get("/trading/v1/profile")

    @transaction.atomic
    def save_connection(
        self,
        token: dict[str, Any],
    ) -> DerivConnection:
        """
        Save the OAuth connection and synchronize trading accounts.
        """

        logger.info("=" * 80)
        logger.info("Saving Deriv connection...")

        expires_at = timezone.now() + timezone.timedelta(
            seconds=token.get("expires_in", 3600),
        )

        accounts = self.get_trading_accounts()

        if not accounts:
            raise ValueError("No trading accounts returned by Deriv.")

        primary_account = accounts[0]

        connection, created = DerivConnection.objects.update_or_create(
            access_token=token["access_token"],
            defaults={
                "token_type": token.get("token_type", "Bearer"),
                "scopes": token.get("scope", ""),
                "token_expires_at": expires_at,
                "is_connected": True,
                "last_synced": timezone.now(),
                "raw_token": token,
            },
        )

        logger.info(
            "Connection saved. Created=%s",
            created,
        )

        logger.info("Synchronizing %s trading accounts...", len(accounts))

        for account in accounts:

            trading_account, created = (
                DerivTradingAccount.objects.update_or_create(
                    account_id=account["account_id"],
                    defaults={
                        "connection": connection,
                        "account_type": account["account_type"],
                        "currency": account["currency"],
                        "balance": account["balance"],
                        "group": account["group"],
                        "status": account["status"],
                        "raw_data": account,
                    },
                )
            )

            logger.info(
                "Account synchronized: %s (%s) Created=%s",
                trading_account.account_id,
                trading_account.account_type,
                created,
            )

        logger.info("Synchronization complete.")
        logger.info("=" * 80)

        return connection

    def get_balance(self) -> dict[str, Any]:
        logger.info("Fetching balance...")
        return self._get("/trading/v1/balance")

    def get_settings(self) -> dict[str, Any]:
        logger.info("Fetching settings...")
        return self._get("/trading/v1/settings")

    def get_limits(self) -> dict[str, Any]:
        logger.info("Fetching limits...")
        return self._get("/trading/v1/limits")

    def get_currencies(self) -> dict[str, Any]:
        logger.info("Fetching currencies...")
        return self._get("/trading/v1/currencies")

    def ping(self) -> dict[str, Any]:
        logger.info("Running Deriv ping...")
        return self.get_profile()

    # ----------------------------------------------------
    # DATABASE
    # ---------------------------------------------------
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
