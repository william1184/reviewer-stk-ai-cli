import logging
import os
import time

import requests

from src.config.env_config import EnvConfig
from src.exceptions.authentication_error import AuthenticationError
from src.exceptions.integration_contract_error import IntegrationContractError
from src.exceptions.integration_error import IntegrationError
from src.exceptions.service_permission_error import ServicePermissionError
from src.service.stk_token_service import StkTokenService
from src.utils.constants import APPLICATION_NAME

logger = logging.getLogger(APPLICATION_NAME)


class StkCallbackService:
    _stk_token_service: StkTokenService
    _url: str
    _retry_count_callback: int
    _retry_timeout: int
    _proxies = None

    def __init__(self, env_config: EnvConfig = None, stk_token_service=None):
        self._stk_token_service = stk_token_service
        self._url = env_config.get_host_stk_ai() + "/v1/quick-commands/callback/{execution_id}"
        self._retry_count_callback = int(env_config.get_stk_retry_count_callback())
        self._retry_timeout = int(env_config.get_stk_retry_timeout())
        self._proxies = env_config.get_proxies()

    def find(self, execution_id: str):
        logger.info(f"Starting search for STK AI response")
        url = self._url.format(execution_id=execution_id)
        headers = self._fill_headers()

        try:
            with requests.Session() as client:
                for attempt in range(self._retry_count_callback, 0, -1):
                    time.sleep(self._retry_timeout)

                    response = client.request(
                        "GET", url=url, headers=headers, proxies=self._proxies
                    )

                    if response.ok:
                        execution_data = response.json()

                        if execution_data["progress"]["status"] == "COMPLETED":
                            logger.info(
                                f"Execution {execution_id} was successfully completed"
                            )

                            return {
                                "execution_id": execution_id,
                                "conversation_id": execution_data["conversation_id"],
                                "review": execution_data["result"],
                            }
                        elif execution_data["progress"]["status"] == "RUNNING":
                            execution_percentage = (
                                    int(execution_data["progress"]["execution_percentage"])
                                    * 100
                            )
                            logger.info(
                                f"Processing {execution_id} is {execution_percentage}% complete...."
                            )
                            continue
                        else:
                            logger.error(
                                f"Progress status invalid",
                                extra={"data": execution_data},
                            )
                            return {
                                "execution_id": execution_id,
                                "conversation_id": execution_data["conversation_id"],
                                "review": f"Progress status invalid, try another execution later...{execution_id}",
                            }

                    response.raise_for_status()
            raise ValueError("Maximum number of attempts reached")
        except requests.exceptions.HTTPError as e:
            logger.error("Failed to integrate with STK AI result")
            response = e.response
            if e.response.status_code == 400:
                raise IntegrationContractError(
                    f"API contract failure for STK AI result: {response.text}"
                )

            if e.response.status_code == 401:
                raise AuthenticationError(
                    f"Authentication failure with STK AI result API: {response.text}"
                )

            if e.response.status_code == 403:
                raise ServicePermissionError(
                    f"Permission failure with STK AI result API: {response.text}"
                )

            raise IntegrationError(
                f"Failed to integrate with STK AI result API: status_code: {response.status_code}"
                f' message: {response.text or "No message"}'
            )
        except Exception as e:
            logger.error(f"Error fetching result for {execution_id}: {e.args[0]}")
            raise
        finally:
            logger.info("Callback execution ended!")

    def _fill_headers(self):
        return {"Authorization": self._stk_token_service.generate_token()}


__all__ = ["StkCallbackService"]
