from typing import Any
import logging

import requests

from django.conf import settings

from apps.deriv.models import DerivTradingAccount

logger = logging.getLogger(__name__)


class DerivOTPService:
    """
    Generates a one-time password (OTP) for establishing an
    authenticated Deriv Options WebSocket connection.
    """

    def __init__(self, trading_account: DerivTradingAccount):
        self.trading_account = trading_account
        self.connection = trading_account.connection

        self.base_url = settings.DERIV_API_BASE.rstrip("/")

        self.headers = {
            "Authorization": (f"Bearer {self.connection.access_token}"),
            "Deriv-App-ID": settings.DERIV_CLIENT_ID,
            "Accept": "application/json",
        }

    def generate_websocket_url(self) -> str:
        """
        Generate an authenticated WebSocket URL
        for the selected trading account.
        """

        endpoint = (
            f"{self.base_url}/trading/v1/options/accounts/"
            f"{self.trading_account.account_id}/otp"
        )

        logger.info("=" * 80)
        logger.info("Generating WebSocket OTP...")
        logger.info("Endpoint: %s", endpoint)
        logger.info("Account ID: %s", self.trading_account.account_id)

        response = requests.post(
            endpoint,
            headers=self.headers,
            timeout=30,
        )

        logger.info("HTTP Status: %s", response.status_code)
        logger.info("Response: %s", response.text)

        response.raise_for_status()

        payload = response.json()

        data = payload.get("data")

        if not data:
            raise ValueError("Missing 'data' in OTP response.")

        websocket_url = data.get("url")

        if not websocket_url:
            raise ValueError("Missing WebSocket URL in OTP response.")

        logger.info("Successfully generated WebSocket URL.")

        return websocket_url
