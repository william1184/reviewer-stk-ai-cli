# StackSpot AI Code Review Tool

This tool uses StackSpot AI to generate code review reports based on specified parameters. Below is a detailed
description of the command-line arguments you can use.

## Command-Line Arguments

### Required Arguments

- `--quick_command_id`: (Optional) Remote quick command identifier on the STK AI portal. Environment Variable:
  CR_STK_AI_ID_QUICK_COMMAND

### Authentication Arguments

- `--client_id`: (Required) Client ID generated on the StackSpot AI platform. Environment Variable: CR_STK_AI_CLIENT_ID
- `--client_secret`: (Required) Client secret generated on the StackSpot AI platform. Environment Variable:
  CR_STK_AI_CLIENT_SECRET

### Retry Configuration

- `--retry_max_attempt`: (Optional) Number of retries to wait for the callback. Default is 10.
- `--retry_timeout`: (Optional) Wait time in seconds between response checks. Default is 10.

### Branch Configuration

- `--base_branch`: (Required) The Branch that should be the base for diff.
- `--compare_branch`: (Required) The Branch should be compared to the base for diff.

### Directory and File Configuration

- `--directory`: (Optional) Path to the directory where the files are located. Default is `.`.
- `--extension`: (Optional) File extension to be reviewed. Default is `.py`.
- `--ignored_files`: (Optional) List of files to ignore. Default: ["venv", ".git", "pytest_cache", "__pycache__"]
- `--ignored_directories`: (Optional) List of directories to ignore. Default: ["setup.py", "manage.py", "__init__.py"]

### Report Configuration

- `--report_directory`: (Optional) Directory where the report will be saved. Default is `report`.
- `--report_filename`: (Optional) Report file name. Default is `code-report.md`.

### Proxy Configuration

- `--http_proxy`: (Optional) HTTP proxy for requests.
- `--https_proxy`: (Optional) HTTPS proxy for requests.

### Realm Configuration

- `--realm`: (Optional) Domain where the token will be generated. Default is `zup`.

### Version

- `--version`: Prints the version of the tool.

## Example Usage

```sh
python your_script.py --client_id YOUR_CLIENT_ID --client_secret YOUR_CLIENT_SECRET --base_branch main --compare_branch feature
```
DEFAULT_IGNORED_DIRECTORIES = {}
DEFAULT_IGNORED_FILES = {"setup.py", "manage.py", "__init__.py"}