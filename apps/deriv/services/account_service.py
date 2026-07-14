from typing import Any, cast
import logging

import requests

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.deriv.models import DerivAccount


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

    def get_primary_account(self) -> dict[str, Any]:
        """
        Returns the primary trading account.
        """

        logger.info("Selecting primary account...")

        accounts = self.get_accounts()

        logger.info("Accounts response:")
        logger.info(accounts)

        if isinstance(accounts, list):
            logger.info("Accounts response is a list.")

            if not accounts:
                raise ValueError("Deriv returned an empty accounts list.")

            account = cast(list[dict[str, Any]], accounts)[0]

        elif "accounts" in accounts:
            logger.info("Accounts response contains 'accounts' key.")

            if not accounts["accounts"]:
                raise ValueError("Accounts array is empty.")

            account = accounts["accounts"][0]

        else:
            logger.info("Accounts response is a single object.")
            account = accounts

        logger.info("Primary account selected:")
        logger.info(account)

        return account

    def get_profile(self) -> dict[str, Any]:
        """
        Get trader profile.
        """

        logger.info("Fetching profile...")

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

        logger.info("Creating account with payload:")
        logger.info(payload)

        return self._post(
            "/trading/v1/options/accounts",
            payload,
        )

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

        logger.info("=" * 80)
        logger.info("Saving Deriv account...")
        logger.info("Raw account data:")
        logger.info(account_data)

        expires_at = timezone.now() + timezone.timedelta(
            seconds=expires_in,
        )

        logger.info("Expires at: %s", expires_at)

        logger.info("Available account keys:")
        logger.info(list(account_data.keys()))

        logger.info("loginid: %s", account_data.get("loginid"))
        logger.info("user_id: %s", account_data.get("user_id"))
        logger.info("email: %s", account_data.get("email"))
        logger.info("currency: %s", account_data.get("currency"))
        logger.info("country: %s", account_data.get("country"))
        logger.info("landing_company: %s", account_data.get("landing_company"))
        logger.info("is_virtual: %s", account_data.get("is_virtual"))

        try:
            account, created = DerivAccount.objects.update_or_create(
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

            logger.info(
                "Database save successful. Created=%s LoginID=%s",
                created,
                account.login_id,
            )

            logger.info("=" * 80)

            return account

        except Exception:
            logger.exception("Failed to save Deriv account.")
            raise

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
