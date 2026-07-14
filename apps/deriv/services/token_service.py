import logging

import requests

from django.conf import settings

logger = logging.getLogger(__name__)


class DerivTokenService:
    @staticmethod
    def exchange_code(code: str, code_verifier: str) -> dict:
        """
        Exchange an OAuth authorization code for an access token.
        """

        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.DERIV_CLIENT_ID,
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": settings.DERIV_REDIRECT_URI,
        }

        logger.info("=" * 80)
        logger.info("DERIV TOKEN EXCHANGE STARTED")
        logger.info("Token URL: %s", settings.DERIV_TOKEN_URL)
        logger.info("Client ID: %s", settings.DERIV_CLIENT_ID)
        logger.info("Redirect URI: %s", settings.DERIV_REDIRECT_URI)
        logger.info("Grant Type: authorization_code")
        logger.info(
            "Authorization code received: %s", code[:12] + "..." if code else None
        )
        logger.info(
            "Code verifier received: %s",
            code_verifier[:12] + "..." if code_verifier else None,
        )

        try:
            response = requests.post(
                settings.DERIV_TOKEN_URL,
                data=payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=30,
            )

            logger.info("TOKEN HTTP STATUS: %s", response.status_code)
            logger.info("TOKEN RESPONSE BODY: %s", response.text)

            response.raise_for_status()

            token_data = response.json()

            logger.info("TOKEN RESPONSE JSON: %s", token_data)

            if "access_token" in token_data:
                logger.info("Access token received successfully.")
                logger.info(
                    "Access token: %s...",
                    token_data["access_token"][:15],
                )

            logger.info("Expires in: %s", token_data.get("expires_in"))
            logger.info("Scope: %s", token_data.get("scope"))
            logger.info("Token type: %s", token_data.get("token_type"))
            logger.info("=" * 80)

            return token_data

        except requests.HTTPError:
            logger.exception("HTTP error occurred during Deriv token exchange.")
            raise

        except requests.RequestException:
            logger.exception("Network error occurred during Deriv token exchange.")
            raise

        except ValueError:
            logger.exception("Failed to parse token response as JSON.")
            raise

        except Exception:
            logger.exception("Unexpected error during Deriv token exchange.")
            raise
