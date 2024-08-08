import logging
import os
from datetime import datetime, timedelta

import requests

from src.config.env_config import EnvConfig
from src.exceptions.authentication_error import AuthenticationError
from src.exceptions.integration_contract_error import IntegrationContractError
from src.exceptions.integration_error import IntegrationError
from src.utils.constants import APPLICATION_NAME

logger = logging.getLogger(APPLICATION_NAME)


class StkTokenService:
    _url: str
    _realm: str
    _client_id: str
    _client_secret: str
    _token_cache: str = None
    _expires_in = None
    _proxies = None

    def __init__(self, env_config: EnvConfig):
        self._client_id = env_config.get_stk_client_id()
        self._client_secret = env_config.get_stk_client_secret()
        self._proxies = env_config.get_proxies()
        self._realm = env_config.get_stk_realm()
        self._url = f"{env_config.get_host_token_stk_ai()}/{self._realm}/oidc/oauth/token"

    def generate_token(self):
        logger.debug(f"Starting token generation for domain: {self._realm}")

        if self._token_cache is not None and not self.is_token_expired():
            return self._token_cache

        try:
            headers = self._fill_headers()

            data = {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "client_credentials",
            }

            with requests.Session() as client:

                response = client.post(
                    url=self._url, data=data, headers=headers, proxies=self._proxies
                )

                if response.ok:
                    token_data = response.json()
                    self._token_cache = (
                        f'{token_data["token_type"]} {token_data["access_token"]}'
                    )
                    self._expires_in = self.get_expiration_date(
                        token_data["expires_in"]
                    )

                    logger.debug("Token Generated")

                    return self._token_cache

                response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error("Failed to integrate with token API")
            response = e.response
            if e.response.status_code == 400:
                raise IntegrationContractError(
                    f"Contract failure with token API: {response.text}"
                )

            if e.response.status_code == 401:
                raise AuthenticationError(
                    f"Authentication failure with token API: {response.text}"
                )

            raise IntegrationError(
                f"Failed to generate access token: status_code: {response.status_code}"
                f' message: {response.text or "No message"}'
            )
        except Exception as e:
            logger.exception(f"Failed to generate access token: {e.args[0]}")
            raise
        finally:
            logger.info("Token execution ended!")

    def is_token_expired(self):
        return self._expires_in < datetime.now()

    @staticmethod
    def get_expiration_date(seconds: int):
        return datetime.now() + timedelta(
            0, seconds
        )  # days, seconds, then other fields.

    @staticmethod
    def _fill_headers():
        return {"Content-Type": "application/x-www-form-urlencoded"}


__all__ = ["StkTokenService"]
