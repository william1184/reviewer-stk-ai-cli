import os
import time
import unittest
from unittest import TestCase
from unittest.mock import Mock

import requests_mock
from requests_mock import Mocker

from src.exceptions.authentication_error import AuthenticationError
from src.exceptions.integration_contract_error import IntegrationContractError
from src.exceptions.integration_error import IntegrationError
from src.service.stk_token_service import StkTokenService
from unit_tests.files.mock import read_json_file


class TestStkTokenService(TestCase):
    _mock_env_config: Mock = None
    _service = None

    def setUp(self):
        self._mock_env_config = Mock()
        self._mock_env_config.get_stk_client_id.return_value = "client_id_value"
        self._mock_env_config.get_stk_client_secret.return_value = "client_secret_value"
        self._mock_env_config.get_proxies.return_value = {}
        self._mock_env_config.get_stk_realm.return_value = "realm_value"
        self._mock_env_config.get_host_token_stk_ai.return_value = "http://localhost:8080"

        self._service = StkTokenService(env_config=self._mock_env_config)

    @requests_mock.Mocker()
    def test__when_required_fields_filled__then_return_token(
            self, mock_request: Mocker
    ):
        # arrange
        mock_request.post(
            url="http://localhost:8080/realm_value/oidc/oauth/token",
            status_code=200,
            json=read_json_file("response/stk_token_service/success.json"),
        )
        # act
        token = self._service.generate_token()

        # assert
        self.assertEqual("Bearer access_token_value", token)

    @requests_mock.Mocker()
    def test__when_required_fields_filled_should_reuse_token__then_return_token(
            self, mock_request: Mocker
    ):
        # arrange
        mock_request.post(
            "http://localhost:8080/realm_value/oidc/oauth/token",
            [
                {
                    "json": read_json_file("response/stk_token_service/success.json"),
                    "status_code": 200,
                },
                {
                    "json": read_json_file(
                        "response/stk_token_service/success_expired.json"
                    ),
                    "status_code": 200,
                },
            ],
        )
        # act
        token_1 = self._service.generate_token()

        token_reuse = self._service.generate_token()

        # assert
        self.assertEqual("Bearer access_token_value", token_1)
        self.assertEqual("Bearer access_token_value", token_reuse)

    @requests_mock.Mocker()
    def test__when_token_expires_should_get_a_new_token__then_return_token(
            self, mock_request: Mocker
    ):
        # arrange
        mock_request.post(
            "http://localhost:8080/realm_value/oidc/oauth/token",
            [
                {
                    "json": read_json_file(
                        "response/stk_token_service/success_expired.json"
                    ),
                    "status_code": 200,
                },
                {
                    "json": read_json_file("response/stk_token_service/success.json"),
                    "status_code": 200,
                },
            ],
        )
        # act
        expired_token = self._service.generate_token()
        time.sleep(1)
        new_token = self._service.generate_token()

        # assert
        self.assertEqual("Bearer access_token_value_2", expired_token)
        self.assertEqual("Bearer access_token_value", new_token)

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_returns_400__then_return_error(
            self, mock_request: Mocker
    ):
        # arrange
        mock_request.post(
            url="http://localhost:8080/realm_value/oidc/oauth/token",
            status_code=400,
            json=read_json_file("response/stk_token_service/error_400.json"),
        )
        # act
        with self.assertRaises(IntegrationContractError) as ctx:
            self._service.generate_token()

        # assert
        self.assertIn("Contract failure with token API", ctx.exception.args[0])

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_returns_401__then_return_error(
            self, mock_request: Mocker
    ):
        # arrange
        mock_request.post(
            url="http://localhost:8080/realm_value/oidc/oauth/token",
            status_code=401,
            json=read_json_file("response/stk_token_service/error_401.json"),
        )
        # act
        with self.assertRaises(AuthenticationError) as ctx:
            self._service.generate_token()

        # assert
        self.assertEqual(
            'Authentication failure with token API: {"error": "invalid_client"}',
            ctx.exception.args[0],
        )

    @requests_mock.Mocker()
    def test__when_required_fields_filled_and_returns_500__then_return_error(
            self, mock_request: Mocker
    ):
        # arrange
        mock_request.post(
            url="http://localhost:8080/realm_value/oidc/oauth/token",
            status_code=500,
        )
        # act
        with self.assertRaises(IntegrationError) as ctx:
            self._service.generate_token()

        # assert
        self.assertEqual(
            "Failed to generate access token: status_code: 500 message: No message",
            ctx.exception.args[0],
        )


if __name__ == "__main__":
    unittest.main()
