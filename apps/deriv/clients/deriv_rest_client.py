import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class DerivRESTClient:
    """
    Base REST client for communicating with the Deriv REST API.

    Responsibilities
    ----------------
    - Builds request URLs
    - Injects authentication headers
    - Handles HTTP errors
    - Parses JSON responses
    - Provides structured logging
    """

    DEFAULT_TIMEOUT = 30

    def __init__(self, access_token: str):
        self.access_token = access_token

        self.base_url = settings.DERIV_API_BASE.rstrip("/")

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Deriv-App-ID": settings.DERIV_CLIENT_ID,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _log_request(
        self,
        method: str,
        url: str,
        payload: Any = None,
        params: Any = None,
    ) -> None:
        logger.info("=" * 80)
        logger.info("DERIV %s REQUEST", method)
        logger.info("URL: %s", url)

        if params is not None:
            logger.info("Params: %s", params)

        if payload is not None:
            logger.info("Payload: %s", payload)

        logger.info(
            "Headers: %s",
            {
                **self.headers,
                "Authorization": "Bearer ********",
            },
        )

    def _log_response(self, response: requests.Response) -> None:
        logger.info("HTTP STATUS: %s", response.status_code)
        logger.info("RESPONSE TEXT: %s", response.text)

    # ------------------------------------------------------------------
    # Core request
    # ------------------------------------------------------------------

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        data: dict | None = None,
    ) -> dict[str, Any]:

        url = self._url(endpoint)

        self._log_request(
            method=method,
            url=url,
            payload=json or data,
            params=params,
        )

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=self.headers,
                params=params,
                json=json,
                data=data,
                timeout=self.DEFAULT_TIMEOUT,
            )

            self._log_response(response)

            response.raise_for_status()

            if not response.text:
                logger.info("Empty response received.")
                logger.info("=" * 80)
                return {}

            body = response.json()

            logger.info("PARSED JSON:")
            logger.info(body)
            logger.info("=" * 80)

            return body

        except requests.HTTPError:
            logger.exception("Deriv returned an HTTP error.")
            raise

        except requests.Timeout:
            logger.exception("Request to Deriv timed out.")
            raise

        except requests.ConnectionError:
            logger.exception("Unable to connect to Deriv.")
            raise

        except Exception:
            logger.exception("Unexpected Deriv REST client error.")
            raise

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------

    def get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict[str, Any]:

        return self.request(
            "GET",
            endpoint,
            params=params,
        )

    def post(
        self,
        endpoint: str,
        payload: dict | None = None,
    ) -> dict[str, Any]:

        return self.request(
            "POST",
            endpoint,
            json=payload,
        )

    def put(
        self,
        endpoint: str,
        payload: dict | None = None,
    ) -> dict[str, Any]:

        return self.request(
            "PUT",
            endpoint,
            json=payload,
        )

    def patch(
        self,
        endpoint: str,
        payload: dict | None = None,
    ) -> dict[str, Any]:

        return self.request(
            "PATCH",
            endpoint,
            json=payload,
        )

    def delete(
        self,
        endpoint: str,
    ) -> dict[str, Any]:

        return self.request(
            "DELETE",
            endpoint,
        )
