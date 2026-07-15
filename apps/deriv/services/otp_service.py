import logging

from apps.deriv.clients.deriv_rest_client import DerivRESTClient

logger = logging.getLogger(__name__)


class DerivOTPService:
    """
    Generates a temporary authenticated WebSocket URL
    for a specific Deriv trading account.
    """

    def __init__(self, access_token: str):
        self.client = DerivRESTClient(access_token)

    def generate(self, account_id: str) -> dict:

        logger.info("=" * 80)
        logger.info("Generating OTP for account %s", account_id)

        response = self.client.post(f"/trading/v1/options/accounts/{account_id}/otp")

        logger.info("OTP Response:")
        logger.info(response)

        data = response.get("data")

        if not data:
            raise ValueError("Deriv returned no data object.")

        websocket_url = data.get("url")

        if not websocket_url:
            raise ValueError("Deriv returned no websocket URL.")

        logger.info("WebSocket URL generated successfully.")
        logger.info("=" * 80)

        return {
            "account_id": account_id,
            "websocket_url": websocket_url,
        }
