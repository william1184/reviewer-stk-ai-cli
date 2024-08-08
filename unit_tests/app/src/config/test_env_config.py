import unittest
from unittest import TestCase

from src.config.env_config import EnvConfig


class TestEnvConfig(TestCase):

    def test_all_properties_filled_without_proxy_then_return_success(self):
        args = {
            "quick_command_id": "code-review-python-en",
            "client_id": "c_id",
            "client_secret": "c_secret",
            "realm": "zup",
            "retry_max_attempts": "10",
            "retry_timeout": "10",
            "http_proxy": "",
            "https_proxy": "",
            "host_stk_ai": "localhost:8080",
            "host_token_stk_ai": "localhost:8081"
        }

        config = EnvConfig(args=args)

        self.assertEqual("code-review-python-en", config.get_stk_id_quick_command())
        self.assertEqual("c_id", config.get_stk_client_id())
        self.assertEqual("c_secret", config.get_stk_client_secret())
        self.assertEqual("zup", config.get_stk_realm())
        self.assertEqual("10", config.get_stk_retry_count_callback())
        self.assertEqual("10", config.get_stk_retry_timeout())
        self.assertEqual(
            {},
            config.get_proxies(),
        )
        self.assertEqual("localhost:8080", config.get_host_stk_ai())
        self.assertEqual("localhost:8081", config.get_host_token_stk_ai())

    def test_all_properties_filled_with_proxy_then_return_success(self):
        args = {
            "quick_command_id": "code-review-python-en",
            "client_id": "c_id",
            "client_secret": "c_secret",
            "realm": "zup",
            "retry_max_attempts": "10",
            "retry_timeout": "10",
            "http_proxy": "http://proxy.com",
            "https_proxy": "https://proxy.com",
            "host_stk_ai": "localhost:8080",
            "host_token_stk_ai": "localhost:8081"
        }

        config = EnvConfig(args=args)

        self.assertEqual("code-review-python-en", config.get_stk_id_quick_command())
        self.assertEqual("c_id", config.get_stk_client_id())
        self.assertEqual("c_secret", config.get_stk_client_secret())
        self.assertEqual("zup", config.get_stk_realm())
        self.assertEqual("10", config.get_stk_retry_count_callback())
        self.assertEqual("10", config.get_stk_retry_timeout())
        self.assertEqual(
            {"http://": "http://proxy.com", "https://": "https://proxy.com"},
            config.get_proxies(),
        )
        self.assertEqual("localhost:8080", config.get_host_stk_ai())
        self.assertEqual("localhost:8081", config.get_host_token_stk_ai())


if __name__ == "__main__":
    unittest.main()
