from typing import Dict


class EnvConfig:
    _stk_quick_command_id: str
    _stk_client_id: str
    _stk_client_secret: str
    _stk_realm: str
    _stk_retry_max_attempts: str
    _stk_retry_timeout: str
    _proxies: Dict

    _host_token_stk_ai: str
    _host_stk_ai: str

    def __init__(self, args: Dict):
        self._stk_quick_command_id = args['quick_command_id']
        self._stk_client_id = args['client_id']
        self._stk_client_secret = args['client_secret']
        self._stk_realm = args['realm']
        self._stk_retry_max_attempts = args['retry_max_attempts']
        self._stk_retry_timeout = args['retry_timeout']

        self._proxies = {}
        if args['http_proxy'] is not None and len(args['http_proxy']) > 0:
            self._proxies["http://"] = args['http_proxy']

        if args['https_proxy'] is not None and len(args['https_proxy']) > 0:
            self._proxies["https://"] = args['https_proxy']

        self._host_stk_ai = args['host_stk_ai']
        self._host_token_stk_ai = args['host_token_stk_ai']

    def get_stk_id_quick_command(self) -> str:
        return self._stk_quick_command_id

    def get_stk_client_id(self) -> str:
        return self._stk_client_id

    def get_stk_client_secret(self) -> str:
        return self._stk_client_secret

    def get_stk_realm(self) -> str:
        return self._stk_realm

    def get_stk_retry_count_callback(self) -> str:
        return self._stk_retry_max_attempts

    def get_stk_retry_timeout(self) -> str:
        return self._stk_retry_timeout

    def get_proxies(self) -> Dict[str, str]:
        return self._proxies

    def get_host_stk_ai(self) -> str:
        return self._host_stk_ai

    def get_host_token_stk_ai(self) -> str:
        return self._host_token_stk_ai


__all__ = ["EnvConfig"]
