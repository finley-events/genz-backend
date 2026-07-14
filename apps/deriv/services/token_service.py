import requests

from django.conf import settings


class DerivTokenService:
    """
    Handles exchanging Deriv OAuth authorization codes
    for access tokens.
    """

    @staticmethod
    def exchange_code(
        code: str,
        code_verifier: str,
    ) -> dict:
        """
        Exchange authorization code for Deriv access token
        using PKCE.
        """

        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.DERIV_CLIENT_ID,
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": settings.DERIV_REDIRECT_URI,
        }

        try:
            response = requests.post(
                settings.DERIV_TOKEN_URL,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )

        except requests.RequestException as exc:
            raise Exception(f"Unable to connect to Deriv token endpoint: {exc}")

        if not response.ok:
            raise Exception(
                f"Deriv token exchange failed "
                f"({response.status_code}): {response.text}"
            )

        data = response.json()

        if "access_token" not in data:
            raise Exception(f"Deriv response missing access token: {data}")

        return data
