import requests

from django.conf import settings


class DerivTokenService:

    @staticmethod
    def exchange_code(
        code: str,
        code_verifier: str,
    ):
        """
        Exchange an authorization code
        for an OAuth access token.
        """

        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.DERIV_CLIENT_ID,
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": settings.DERIV_REDIRECT_URI,
        }

        response = requests.post(
            settings.DERIV_TOKEN_URL,
            data=payload,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()
