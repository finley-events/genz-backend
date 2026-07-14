import requests

from django.conf import settings

import requests
from django.conf import settings


class DerivTokenService:

    @staticmethod
    def exchange_code(code, code_verifier):

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
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )

        print("TOKEN STATUS:", response.status_code)
        print("TOKEN RESPONSE:", response.text)

        response.raise_for_status()

        return response.json()
