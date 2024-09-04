import unittest
from unittest import TestCase
from unittest.mock import Mock, MagicMock

import requests_mock
from requests_mock import Mocker

from reviewer_stk_ai.src.exceptions.authentication_error import AuthenticationError
from reviewer_stk_ai.src.exceptions.integration_contract_error import (
    IntegrationContractError,
)
from reviewer_stk_ai.src.exceptions.integration_error import IntegrationError
from reviewer_stk_ai.src.service.stk_execution_service import StkExecutionService
from unit_tests.files.mock import read_json_file


class TestStkExecutionService(TestCase):
    _mock_env_config: Mock = None
    _mock_stk_token_service = None
    _service = None

    def setUp(self):
        self._mock_env_config = Mock()
        self._mock_stk_token_service = MagicMock()

        self._mock_env_config.get_stk_id_quick_command.return_value = (
            "quick-command-remote"
        )
        self._mock_env_config.get_stk_client_id.return_value = "client_id_value"
        self._mock_env_config.get_stk_client_secret.return_value = "client_secret_value"
        self._mock_env_config.get_proxies.return_value = {}
        self._mock_env_config.get_stk_realm.return_value = "realm_value"
        self._mock_env_config.get_host_stk_ai.return_value = "http://localhost:8081"

        self._service = StkExecutionService(
            env_config=self._mock_env_config,
            stk_token_service=self._mock_stk_token_service,
        )

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_with_conversation_id__then_return_execution_id(
        self, mock_request: Mocker
    ):
        # arrange
        self._mock_stk_token_service.generate_token.return_value = "bearer token"
        mock_request.post(
            url="http://localhost:8081/v1/quick-commands/create-execution/quick-command-remote",
            status_code=200,
            request_headers={"conversation_id": "01HYRHKFPF9PNNJQ91AKRX98PZ"},
            json=read_json_file("response/stk_execution_service/success.json"),
        )
        # act
        execution_id = self._service.create(
            file_content="content", conversation_id="01HYRHKFPF9PNNJQ91AKRX98PZ"
        )

        # assert
        self.assertEqual("01HYRHKFPFAZK1FFF8HVKWYEDN", execution_id)
        self._mock_stk_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_without_conversation_id__then_return_execution_id(
        self, mock_request: Mocker
    ):
        # arrange
        self._mock_stk_token_service.generate_token.return_value = "bearer token"
        mock_request.post(
            url="http://localhost:8081/v1/quick-commands/create-execution/quick-command-remote",
            status_code=200,
            json=read_json_file("response/stk_execution_service/success.json"),
        )
        # act
        execution_id = self._service.create(file_content="content")

        # assert
        self.assertEqual("01HYRHKFPFAZK1FFF8HVKWYEDN", execution_id)
        self._mock_stk_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_return_400__then_return_error(
        self, mock_request: Mocker
    ):
        # arrange
        self._mock_stk_token_service.generate_token.return_value = "bearer token"

        mock_request.post(
            url="http://localhost:8081/v1/quick-commands/create-execution/quick-command-remote",
            status_code=400,
            json=read_json_file("response/stk_execution_service/error_400.json"),
        )
        # act
        with self.assertRaises(IntegrationContractError) as ctx:
            self._service.create(file_content="content")

        # assert
        self.assertIn("Execution API contract failure", ctx.exception.args[0])
        self._mock_stk_token_service.generate_token.assert_called_once()
        self.assertEqual(1, mock_request.call_count)

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_return_401__then_return_error(
        self, mock_request: Mocker
    ):
        # arrange
        self._mock_stk_token_service.generate_token.return_value = "bearer token"

        mock_request.post(
            url="http://localhost:8081/v1/quick-commands/create-execution/quick-command-remote",
            status_code=401,
            json=read_json_file("response/stk_execution_service/error_401.json"),
        )
        # act
        with self.assertRaises(AuthenticationError) as ctx:
            self._service.create(file_content="content")

        # assert
        self.assertIn(
            "Authentication failure with execution API", ctx.exception.args[0]
        )
        self._mock_stk_token_service.generate_token.assert_called_once()

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_return_500__then_return_error(
        self, mock_request: Mocker
    ):
        # arrange
        self._mock_stk_token_service.generate_token.return_value = "bearer token"

        mock_request.post(
            url="http://localhost:8081/v1/quick-commands/create-execution/quick-command-remote",
            status_code=500,
        )
        # act
        with self.assertRaises(IntegrationError) as ctx:
            self._service.create(file_content="content")

        # assert
        self.assertIn("Integration with execution API failed", ctx.exception.args[0])
        self.assertEqual(3, self._mock_stk_token_service.generate_token.call_count)

    @requests_mock.Mocker()
    def test__when_token_generation_fails__then_return_error(
        self, mock_request: Mocker
    ):
        # arrange
        self._mock_stk_token_service.generate_token.side_effect = IntegrationError(
            "Token generation failure"
        )

        # act
        with self.assertRaises(IntegrationError) as ctx:
            self._service.create(file_content="content")

        # assert
        self.assertEqual("Token generation failure", ctx.exception.args[0])
        self.assertEqual(3, self._mock_stk_token_service.generate_token.call_count)
        self.assertEqual(0, mock_request.call_count)


if __name__ == "__main__":
    unittest.main()
