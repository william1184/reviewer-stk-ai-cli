import os
import unittest
from unittest import TestCase
from unittest.mock import Mock

import requests_mock
from requests_mock import Mocker

from src.exceptions.authentication_error import AuthenticationError
from src.exceptions.integration_contract_error import IntegrationContractError
from src.exceptions.integration_error import IntegrationError
from src.exceptions.service_permission_error import ServicePermissionError
from src.service.stk_callback_service import StkCallbackService
from unit_tests.files.mock import read_json_file


class TestStkCallbackService(TestCase):
    _mock_env_config: Mock = None
    _mock_sts_token_service = None
    _service = None

    def setUp(self):
        self._mock_env_config = Mock()
        self._mock_sts_token_service = Mock()

        self._mock_env_config.get_client_id.return_value = "client_id_value"
        self._mock_env_config.get_proxies.return_value = {}
        self._mock_env_config.get_stk_retry_count_callback.return_value = "10"
        self._mock_env_config.get_stk_retry_timeout.return_value = "0"
        self._mock_env_config.get_host_stk_ai.return_value = "http://localhost:8081"

        self._service = StkCallbackService(
            env_config=self._mock_env_config,
            stk_token_service=self._mock_sts_token_service,
        )

    @requests_mock.Mocker()
    def test__when_required_fields_filled__then_return_response(
            self, mock_request: Mocker
    ):
        # arrange
        self._mock_sts_token_service.generate_token.return_value = "bearer token"

        mock_request.get(
            "http://localhost:8081/v1/quick-commands/callback/02HYRHKFPFAZK1FFF8HVKWYEDQ",
            [
                {
                    "json": read_json_file(
                        "response/stk_callback_service/success_running.json"
                    ),
                    "status_code": 200,
                },
                {
                    "json": read_json_file(
                        "response/stk_callback_service/success_complete.json"
                    ),
                    "status_code": 200,
                },
            ],
        )
        # act
        response = self._service.find(execution_id="02HYRHKFPFAZK1FFF8HVKWYEDQ")

        # assert
        self.assertEqual(
            {
                "conversation_id": "01HYRHKFPF9PNNJQ91AKRX98PZ",
                "execution_id": "02HYRHKFPFAZK1FFF8HVKWYEDQ",
                "review": "Points found:\\n'\n"
                          "           'I am not able to perform the code review of this "
                          "file. ",
            },
            response,
        )
        self._mock_sts_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_hits_max_number_of_retries__then_return_error(
            self, mock_request: Mocker
    ):
        # arrange
        self._mock_sts_token_service.generate_token.return_value = "bearer token"
        self._mock_env_config.get_stk_retry_count_callback.return_value = "2"

        mock_request.get(
            "http://localhost:8081/v1/quick-commands/callback/02HYRHKFPFAZK1FFF8HVKWYEDQ",
            [
                {
                    "json": read_json_file(
                        "response/stk_callback_service/success_running.json"
                    ),
                    "status_code": 200,
                }
            ],
        )
        # act
        with self.assertRaises(ValueError) as ctx:
            self._service.find(execution_id="02HYRHKFPFAZK1FFF8HVKWYEDQ")

        # assert
        self.assertEqual("Maximum number of attempts reached", ctx.exception.args[0])
        self._mock_sts_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_return_execution_fail__then_return_response(
            self, mock_request: Mocker
    ):
        # arrange
        self._mock_sts_token_service.generate_token.return_value = "bearer token"

        mock_request.get(
            url="http://localhost:8081/v1/quick-commands/callback/02HYRHKFPFAZK1FFF8HVKWYEDQ",
            status_code=200,
            json=read_json_file(
                "response/stk_callback_service/success_execution_fail.json"
            ),
        )
        # act
        response = self._service.find(execution_id="02HYRHKFPFAZK1FFF8HVKWYEDQ")

        # assert
        self.assertEqual(
            {
                "conversation_id": "01HYRHKFPF9PNNJQ91AKRX98PZ",
                "execution_id": "02HYRHKFPFAZK1FFF8HVKWYEDQ",
                "review": "Progress status invalid, try another execution "
                          "later...02HYRHKFPFAZK1FFF8HVKWYEDQ",
            },
            response,
        )
        self._mock_sts_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_required_fields_filled_with_conversation_id_and_returns_400__then_return_error(
            self, mock_request: Mocker
    ):
        # arrange
        self._mock_sts_token_service.generate_token.return_value = "bearer token"

        mock_request.get(
            url="http://localhost:8081/v1/quick-commands/callback/02HYRHKFPFAZK1FFF8HVKWYEDQ",
            status_code=400,
        )
        # act
        with self.assertRaises(IntegrationContractError) as ctx:
            self._service.find(execution_id="02HYRHKFPFAZK1FFF8HVKWYEDQ")

        # assert
        self.assertIn("API contract failure for STK AI result", ctx.exception.args[0])
        self._mock_sts_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_returns_401__then_return_error(
            self, mock_request: Mocker
    ):
        # arrange
        self._mock_sts_token_service.generate_token.return_value = "bearer token"

        mock_request.get(
            url="http://localhost:8081/v1/quick-commands/callback/02HYRHKFPFAZK1FFF8HVKWYEDQ",
            status_code=401,
        )
        # act
        with self.assertRaises(AuthenticationError) as ctx:
            self._service.find(execution_id="02HYRHKFPFAZK1FFF8HVKWYEDQ")

        # assert
        self.assertIn(
            "Authentication failure with STK AI result API", ctx.exception.args[0]
        )
        self._mock_sts_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_returns_403__then_return_error(
            self, mock_request: Mocker
    ):
        # arrange
        self._mock_sts_token_service.generate_token.return_value = "bearer token"

        mock_request.get(
            url="http://localhost:8081/v1/quick-commands/callback/02HYRHKFPFAZK1FFF8HVKWYEDQ",
            status_code=403,
        )
        # act
        with self.assertRaises(ServicePermissionError) as ctx:
            self._service.find(execution_id="02HYRHKFPFAZK1FFF8HVKWYEDQ")

        # assert
        self.assertIn(
            "Permission failure with STK AI result API", ctx.exception.args[0]
        )
        self._mock_sts_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_returns_500__then_return_error(
            self, mock_request: Mocker
    ):
        # arrange
        self._mock_sts_token_service.generate_token.return_value = "bearer token"

        mock_request.get(
            url="http://localhost:8081/v1/quick-commands/callback/02HYRHKFPFAZK1FFF8HVKWYEDQ",
            status_code=500,
        )
        # act
        with self.assertRaises(IntegrationError) as ctx:
            self._service.find(execution_id="02HYRHKFPFAZK1FFF8HVKWYEDQ")

        # assert
        self.assertIn(
            "Failed to integrate with STK AI result API", ctx.exception.args[0]
        )
        self._mock_sts_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_generate_token_fails__then_return_error(self, mock_request: Mocker):
        # arrange
        self._mock_sts_token_service.generate_token.side_effect = IntegrationError(
            "Failed to generate token"
        )

        # act
        with self.assertRaises(IntegrationError) as ctx:
            self._service.find(execution_id="02HYRHKFPFAZK1FFF8HVKWYEDQ")

        # assert
        self.assertEqual("Failed to generate token", ctx.exception.args[0])
        self._mock_sts_token_service.generate_token.assert_called_once()
        self.assertEqual(0, mock_request.called)


if __name__ == "__main__":
    unittest.main()
