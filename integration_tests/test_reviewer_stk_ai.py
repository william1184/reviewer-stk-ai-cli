import os
import shutil
import subprocess
import sys
import unittest
from unittest import TestCase

current_file = __file__
current_directory = os.path.dirname(os.path.abspath(current_file))
parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(current_file)))
os.chdir(parent_directory)


def run_command(command, check=True):
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode


class TestReviewerStkAi(TestCase):
    _active_command = ""
    _dist_dir = ""
    _venv_dir = ""

    @classmethod
    def setUpClass(cls):
        # Build the project
        print("Building the project...")
        if run_command("poetry build"):
            print("Build failed", file=sys.stderr)
            sys.exit(1)

        # Create a virtual environment
        print("Creating a virtual environment...")
        cls._venv_dir = f"{current_directory}/venv"
        if run_command(f"python -m venv {cls._venv_dir}"):
            print("Failed to create virtual environment", file=sys.stderr)
            raise EnvironmentError("environment create fail")

        # Activate the virtual environment
        if os.name == "nt":  # Windows
            activate_script = os.path.join(
                current_directory, "venv", "Scripts", "activate.bat"
            )
            cls._active_command = f"{activate_script}"
        else:  # Unix-like
            activate_script = os.path.join(current_directory, "venv", "bin", "activate")
            cls._active_command = f"source {activate_script}"

        # Install the built package
        print("Installing the package...")
        cls._dist_dir = os.path.join(parent_directory, "dist")
        wheel_file = [f for f in os.listdir(cls._dist_dir) if f.endswith(".whl")][0]
        if run_command(
            f"{cls._active_command} && pip install {os.path.join(cls._dist_dir, wheel_file)} "
            "--force-reinstall --no-cache-dir"
        ):
            print("Failed to install the package", file=sys.stderr)
            sys.exit(1)

    @classmethod
    def tearDownClass(cls):

        print("Removing directory venv...")
        shutil.rmtree(cls._venv_dir)
        print("Removed directory venv...")

        print("Removing directory dist...")
        shutil.rmtree(cls._dist_dir)
        print("Removed directory dist...")

    def test_cli_version(self):
        result = subprocess.run(
            [
                f"{self._active_command}",
                "&&",
                "python",
                "-m",
                "reviewer_stk_ai",
                "--version",
            ],
            capture_output=True,
            text=True,
        )
        self.assertIn("reviewer_stk_ai, version 1.0.0", result.stdout)

    def test_cli_help(self):
        result = subprocess.run(
            [
                f"{self._active_command}",
                "&&",
                "python",
                "-m",
                "reviewer_stk_ai",
                "--help",
            ],
            capture_output=True,
            text=True,
        )
        self.assertIn(
            "Usage: python -m reviewer_stk_ai [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  "
            "--quick-command-id <string>   Remote quick command identifier on the STK AI\n                             "
            "   portal  [required]\n  --client-id <string>          Client ID generated on the StackSpot AI\n          "
            "                      platform  [required]\n  --client-secret <string>      Client secret generated on the"
            " StackSpot AI\n                                platform  [required]\n  --host-token-stk-ai <string>  Host "
            "of the token api.\n  --host-stk-ai <string>        Host of the stk ai api.\n  --realm <string>            "
            "  Domain where the token will be generated.\n  --retry-max-attempts <int>    Number of retries to wait for"
            " the callback\n  --retry-timeout <int>         Wait time in seconds between response checks.\n  "
            "--http-proxy <string>         HTTP proxy for requests.\n  --https-proxy <string>        HTTPS proxy for "
            "requests.\n  --directory TEXT              Path to the directory where the files are\n                    "
            "            located\n  --extension <string>          File extension to be reviewed\n  --ignored-files TEXT"
            "          List of files to ignore\n  --ignored-directories TEXT    List of directories to ignore\n  "
            "--report-directory <string>   Directory where the report will be saved\n  --report-filename <string>    "
            "Report file name\n  --version                     Show the version and exit.\n  --debug / --no-debug\n  "
            "--help                        Show this message and exit.\n\nCommands:\n  review-changes  Send the changes"
            " for reviewing.\n  review-dir      Send all files on dir for reviewing.\n",
            result.stdout,
        )

    def test_cli_default_command(self):
        result = subprocess.run(
            [
                f"{self._active_command}",
                "&&",
                "python",
                "-m",
                "reviewer_stk_ai",
                "--host-stk-ai",
                "http://localhost:3001",
                "--host-token-stk-ai",
                "http://localhost:3001",
                "--quick-command-id",
                "code-review-python-ptbr",
                "--client-id",
                "123",
                "--client-secret",
                "assa",
            ],
            capture_output=True,
            text=True,
        )
        print(result)
        self.assertIn(
            "report/review-code-report.md.\n",
            result.stdout,
        )

    def test_cli_review_dir_command(self):
        result = subprocess.run(
            [
                f"{self._active_command}",
                "&&",
                "python",
                "-m",
                "reviewer_stk_ai",
                "--host-stk-ai",
                "http://localhost:3001",
                "--host-token-stk-ai",
                "http://localhost:3001",
                "--quick-command-id",
                "code-review-python-ptbr",
                "--client-id",
                "123",
                "--client-secret",
                "assa",
                "--directory",
                f"{current_directory}/files/test_dir",
                "review-dir",
            ],
            capture_output=True,
            text=True,
        )
        print(result)
        self.assertIn(
            "Report file created on report/review-code-report.md",
            result.stdout,
        )

    def test_cli_review_dir_command__with__show(self):
        result = subprocess.run(
            [
                f"{self._active_command}",
                "&&",
                "python",
                "-m",
                "reviewer_stk_ai",
                "--host-stk-ai",
                "http://localhost:3001",
                "--host-token-stk-ai",
                "http://localhost:3001",
                "--quick-command-id",
                "code-review-python-ptbr",
                "--client-id",
                "123",
                "--client-secret",
                "assa",
                "--directory",
                f"{current_directory}/files/test_dir",
                "--show",
                "review-dir",
            ],
            capture_output=True,
            text=True,
        )
        print(result)
        self.assertIn(
            "",
            result.stdout,
        )

    def test_cli_review_changes_command(self):
        result = subprocess.run(
            [
                f"{self._active_command}",
                "&&",
                "python",
                "-m",
                "reviewer_stk_ai",
                "--host-stk-ai",
                "http://localhost:3001",
                "--host-token-stk-ai",
                "http://localhost:3001",
                "--quick-command-id",
                "code-review-python-ptbr",
                "--client-id",
                "123",
                "--client-secret",
                "assa",
                "--directory",
                f"{current_directory}/files/test_changes",
                "review-changes",
            ],
            capture_output=True,
            text=True,
        )

        print(result)

        self.assertIn(
            "Report file created on report/review-code-report.md",
            result.stdout,
        )

    def test_cli_review_changes_command__with_branch_release(self):
        result = subprocess.run(
            [
                f"{self._active_command}",
                "&&",
                "python",
                "-m",
                "reviewer_stk_ai",
                "--host-stk-ai",
                "http://localhost:3001",
                "--host-token-stk-ai",
                "http://localhost:3001",
                "--quick-command-id",
                "code-review-python-ptbr",
                "--client-id",
                "123",
                "--client-secret",
                "assa",
                "--directory",
                f"{current_directory}/files/test_changes",
                "review-changes",
                "--compare-branch",
                "release",
            ],
            capture_output=True,
            text=True,
        )

        print(result)

        self.assertIn(
            "Report file created on report/review-code-report.md",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
