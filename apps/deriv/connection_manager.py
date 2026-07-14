import requests

from django.conf import settings

from apps.deriv.models import DerivAccount


class DerivOTPService:
    """
    Generates a one-time password (OTP) for establishing an
    authenticated Deriv Options WebSocket connection.

    This service does not create the WebSocket connection.
    It only requests a temporary WebSocket URL from the
    Deriv REST API.
    """

    def __init__(self, deriv_account: DerivAccount):
        self.deriv_account = deriv_account

        self.base_url = settings.DERIV_API_BASE.rstrip("/")

        self.headers = {
            "Authorization": f"Bearer {deriv_account.access_token}",
            "Deriv-App-ID": settings.DERIV_CLIENT_ID,
            "Accept": "application/json",
        }

    def generate_websocket_url(self) -> str:
        """
        Request a one-time WebSocket URL for the selected
        trading account.

        Returns:
            str: Authenticated WebSocket URL.
        """

        endpoint = (
            f"{self.base_url}/trading/v1/options/accounts/"
            f"{self.deriv_account.login_id}/otp"
        )

        response = requests.post(
            endpoint,
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

        data = payload.get("data")

        if not data:
            raise ValueError("Missing 'data' in OTP response.")

        websocket_url = data.get("url")

        if not websocket_url:
            raise ValueError("Missing WebSocket URL in OTP response.")

        return websocket_url
