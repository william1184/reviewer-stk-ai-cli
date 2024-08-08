import os
import sys

import pytest

os.environ['LOG_LEVEL'] = 'CRITICAL'


@pytest.fixture(autouse=True)
def clean_env_and_modules():
    # Save the original state of environment variables and loaded modules
    original_env = os.environ.copy()
    original_modules = sys.modules.copy()

    yield

    # Restore the original state of environment variables
    os.environ.clear()
    os.environ.update(original_env)

    if "CR_STK_AI_CLIENT_ID" in os.environ:
        del os.environ["CR_STK_AI_CLIENT_ID"]
    if "CR_STK_AI_CLIENT_SECRET" in os.environ:
        del os.environ["CR_STK_AI_CLIENT_SECRET"]
    if "CR_STK_AI_REALM" in os.environ:
        del os.environ["CR_STK_AI_REALM"]
    if "CR_STK_AI_MAX_ATTEMPTS" in os.environ:
        del os.environ["CR_STK_AI_MAX_ATTEMPTS"]

    # Remove new modules loaded during the test
    for module in list(sys.modules.keys()):
        if module not in original_modules:
            del sys.modules[module]
