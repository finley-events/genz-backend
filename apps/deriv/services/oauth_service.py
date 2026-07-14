from urllib.parse import urlencode

from django.conf import settings

from apps.deriv.utils import generate_pkce_pair


class DerivOAuthService:
    """
    Builds the Deriv OAuth authorization URL.
    """

    def create_authorization(self):

        pkce = generate_pkce_pair()

        params = {
            "response_type": "code",
            "client_id": settings.DERIV_CLIENT_ID,
            "redirect_uri": settings.DERIV_REDIRECT_URI,
            "scope": "trade account_manage",
            "code_challenge": pkce["code_challenge"],
            "code_challenge_method": "S256",
            "state": pkce["state"],
        }
        authorization_url = f"{settings.DERIV_AUTH_URL}" f"?{urlencode(params)}"

        return {
            "authorization_url": authorization_url,
            "state": pkce["state"],
            "code_verifier": pkce["code_verifier"],
        }
