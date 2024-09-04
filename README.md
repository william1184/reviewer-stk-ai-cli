# StackSpot AI CLI

This CLI tool is designed to interact with StackSpot AI for code review and analysis. It is built using Python and
managed with Poetry.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
    - [Review Directory](#Directory)
    - [Review Changes](#Diff)    
- [License](#license)

## Installation

### Prerequisites

- Python 3.8+
- Stackspot AI Account
- Quick command remote

  ```bash
  pip install reviewer_stk_ai
  ```

## Usage

You can use the CLI tool by running the cli.py script. The general command structure is:

```bash
reviewer_stk_ai [OPTIONS] COMMAND [ARGS]...
```

Command Options
The CLI provides several options that can be passed globally or for specific commands:

- `--quick-command-id <string>`: Remote quick command identifier on the STK AI portal (required).
- `--client-id <string>`: Client ID generated on the StackSpot AI platform (required).
- `--client-secret <string>`: Client secret generated on the StackSpot AI platform (required).
- `--realm <string>`: Domain where the token will be generated (default: "zup").
- `--retry-timeout <int>`: Set the wait time (in seconds) between response checks (default: 10 seconds).
- `--retry-max-attempts <int>`: Set the number of retries to wait for the callback (default: 10).
- `--host-stk-ai <string>`: Host of the STK AI API (default: https://genai-code-buddy-api.stackspot.com).
- `--host-token-stk-ai <string>`: Host of the token API (default: https://idm.stackspot.com).
- `--https-proxy <string>`: Set the HTTPS proxy for requests.
- `--http-proxy <string>`: Set the HTTP proxy for requests.

- `--report-filename <string>`: Name of the report file (default: "report.txt").
- `--report-directory <string>`: Directory where the report will be saved (default: "reports").
- `--ignored-directories <string>`: List of directories to ignore.
- `--ignored-files <string>`: List of files to ignore.
- `--extension <string>`: File extension to be reviewed (default: ".py").
- `--directory <string>`: Path to the directory where the files are located (default: ".").
- `--debug/--no-debug`: Enable or disable debug mode.

## Commands



### Directory

This command reviews all files in a specified directory.

### Example:

```bash
reviewer_stk_ai --quick-command-id YOUR_QUICK_COMMAND --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET review_dir --directory ./src
```

### Examples

Reviewing all files in the current directory:

```bash
reviewer_stk_ai --quick-command-id YOUR_QUICK_COMMAND --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

Ignoring specific directories and files during review:

```bash
reviewer_stk_ai --quick-command-id YOUR_QUICK_COMMAND --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --ignored-directories .git --ignored-files config.py
```

Example all parameters fullified

``` bash
reviewer_stk_ai --quick-command-id code-review-python-ptbr --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --realm zup --retry-timeout 8 --retry-max-attempts 3 --host-stk-ai http://localhost:3001 --host-token-stk-ai http://localhost:3001 --https-proxy --https-proxy --report-filename diff_report.txt --report-directory reports --ignored-directories unit_tests --ignored-files __main__.py --extension .py --directory . --debug
```

### Diff

This command reviews changes between two branches in a Git repository. It compares the specified branches and analyzes
the modified files.

#### Options:

- `--base-branch <string>`: The branch that should be the base for comparison (default: "main").
- `--compare-branch <string>`: The branch to compare against the base (default: "develop").

#### Example:

Comparing changes between branches and generating a report:

```bash
reviewer_stk_ai --quick-command-id YOUR_QUICK_COMMAND --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET diff --base-branch main --compare-branch feature-branch
```

#### Example:

Comparing changes between branches and generating a report:

```bash
reviewer_stk_ai --quick-command-id YOUR_QUICK_COMMAND --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET diff --base-branch main --compare-branch feature-branch
```

Example all parameters fullified

``` bash
reviewer_stk_ai --quick-command-id code-review-python-ptbr --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --realm zup --retry-timeout 8 --retry-max-attempts 3 --host-stk-ai http://localhost:3001 --host-token-stk-ai http://localhost:3001 --https-proxy --https-proxy --report-filename diff_report.txt --report-directory reports --ignored-directories unit_tests --ignored-files __main__.py --extension .py --directory . --debug diff --base-branch main --compare-branch feature-branch
```

#### Configuration

You can configure environment variables to set default values for the options:

- `HTTPS_PROXY`, `HTTP_PROXY`: Proxies for requests.
- `CR_STK_AI_RETRY_TIMEOUT`, `CR_STK_AI_MAX_ATTEMPTS`: Retry settings.
- `CR_STK_AI_REALM`, `CR_STK_AI_HOST`, `CR_STK_AI_HOST_TOKEN`: API configuration.
- `CR_STK_AI_CLIENT_ID`, `CR_STK_AI_CLIENT_SECRET`, `CR_STK_AI_ID_QUICK_COMMAND`: Authentication credentials.

### License

This project is licensed under the MIT License. See the LICENSE file for details.