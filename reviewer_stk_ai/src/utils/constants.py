APPLICATION_NAME = "reviewer_stk_ai"

EXIT_FAIL = 1
EXIT_SUCCESS = 0

# Constants for default ignored directories and files
DEFAULT_IGNORED_DIRECTORIES = {"venv", ".git", "pytest_cache", "__pycache__"}
DEFAULT_IGNORED_FILES = {"setup.py", "manage.py", "__init__.py"}

# Constants for default file extension and directories
DEFAULT_EXTENSION = ".py"
DEFAULT_DIRECTORY = "."
DEFAULT_REPORT_DIRECTORY = "report"
DEFAULT_REPORT_FILENAME = "code-report"

# Default

DEFAULT_REALM = "zup"

# MESSAGES
ERROR_MESSAGE_REALM = (
    "The realm is required to connect to STK AI. Provide --realm or the environment variable "
    "CR_STK_AI_REALM"
)
ERROR_MESSAGE_CLIENT_SECRET = (
    "The client_secret is required to connect to STK AI. Provide --client_secret or the "
    "environment variable CR_STK_AI_CLIENT_SECRET"
)
ERROR_MESSAGE_QUICK_COMMAND = "The Remote Quick Command ID is required"
ERROR_MESSAGE_CLIENT_ID = (
    "The client_id is required to connect to STK AI. Provide --client_id or the environment "
    "variable CR_STK_AI_CLIENT_ID"
)
