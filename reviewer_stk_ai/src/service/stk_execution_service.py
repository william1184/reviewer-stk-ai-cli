import logging
import os

import requests

from src.config.env_config import EnvConfig
from src.exceptions.authentication_error import AuthenticationError
from src.exceptions.integration_contract_error import IntegrationContractError
from src.exceptions.integration_error import IntegrationError
from src.service.stk_token_service import StkTokenService
from src.utils.constants import APPLICATION_NAME

logger = logging.getLogger(APPLICATION_NAME)


class StkExecutionService:
    _stk_token_service: StkTokenService
    _url: str
    _id_quick_command: str
    _proxies = None

    def __init__(self, env_config: EnvConfig, stk_token_service=None):
        self._stk_token_service = stk_token_service
        self._url = env_config.get_host_stk_ai() + "/v1/quick-commands/create-execution/{id_quick_command}"
        self._id_quick_command = env_config.get_stk_id_quick_command()
        self._proxies = env_config.get_proxies()

    def create(self, file_content: str, conversation_id: str = None) -> str:
        logger.info("Starting file upload to STK AI")
        url = self._url.format(id_quick_command=self._id_quick_command)
        headers = self._fill_headers(conversation_id=conversation_id)
        file_content = file_content.replace("\n", r"\\n").replace('\\"', r'\\\\"')

        try:
            with requests.Session() as client:
                response = client.request(
                    "POST",
                    url=url,
                    json={"input_data": file_content},
                    headers=headers,
                    proxies=self._proxies,
                )

                if response.ok:
                    logger.info(f"File successfully uploaded: {conversation_id}")
                    return response.text.replace('"', "")

                response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error("Integration with execution API failed")
            response = e.response
            if e.response.status_code == 400:
                raise IntegrationContractError(
                    f"Execution API contract failure: {response.text}"
                )

            if e.response.status_code == 401:
                raise AuthenticationError(
                    f"Authentication failure with execution API: {response.text}"
                )

            raise IntegrationError(
                f"Integration with execution API failed: status_code: {response.status_code}"
                f' message: {response.text or "No message"}'
            )
        except Exception as e:
            logger.error(f"Error processing file upload: {e.args[0]}")
            raise
        finally:
            logger.info("Execution ended!")

    def _fill_headers(self, conversation_id: str):
        headers = {"Authorization": self._stk_token_service.generate_token()}

        if conversation_id:
            headers["conversation_id"] = conversation_id

        return headers


__all__ = ["StkExecutionService"]
