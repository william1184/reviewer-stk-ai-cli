import unittest
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from reviewer_stk_ai.src.exceptions.integration_error import IntegrationError
from reviewer_stk_ai.src.utils.constants import (
    APPLICATION_NAME,
    EXIT_SUCCESS,
    EXIT_FAIL,
)
from src.utils.constants import DEFAULT_REPORT_FILENAME, DEFAULT_REPORT_DIRECTORY


class TestCli(TestCase):
    _mock_find_all_files = None
    _mock_find_all_changed_code = None
    _mock_create_file_and_directory = None
    _mock_review_service = None
    _cli = None

    def setUp(self):
        self._mock_review_service = patch(
            "reviewer_stk_ai.src.service.stk_token_service.StkTokenService"
        ).start()()
        self._mock_review_service = patch(
            "reviewer_stk_ai.src.service.stk_execution_service.StkExecutionService"
        ).start()()
        self._mock_review_service = patch(
            "reviewer_stk_ai.src.service.stk_callback_service.StkCallbackService"
        ).start()()
        self._mock_review_service = patch(
            "reviewer_stk_ai.src.service.reviewer_service.ReviewerService"
        ).start()()

        self._mock_find_all_files = patch(
            "reviewer_stk_ai.src.utils.file_helper.find_all_files"
        ).start()
        self._mock_find_all_changed_code = patch(
            "reviewer_stk_ai.src.utils.git_helper.find_all_changed_code"
        ).start()
        self._mock_create_file_and_directory = patch(
            "reviewer_stk_ai.src.utils.file_helper.create_file_and_directory"
        ).start()

        import cli

        self._cli = cli

        self.runner = CliRunner()

    def tearDown(self):
        # Parar todos os patches
        patch.stopall()

    def test__review_dir__when_has_files__then__return_success(self):
        self._mock_find_all_files.return_value = {
            "/root/dir2\\file_3.py": "file content",
        }

        self._mock_review_service.run.return_value = {
            "b/file1.py": "Points found:\n"
            "I am not able to perform the code review of this file",
        }

        result = self.runner.invoke(
            self._cli.cli,
            [
                "--quick-command-id",
                "test_command",
                "--client-id",
                "test_client-id",
                "--client-secret",
                "test_client-secret",
                "review-dir",
            ],
            prog_name=APPLICATION_NAME,
        )

        self.assertEqual(EXIT_SUCCESS, result.exit_code)

        self._mock_review_service.run.assert_called_once()
        self._mock_find_all_changed_code.assert_not_called()
        self._mock_find_all_files.assert_called_once_with(
            directory=".",
            extension=".py",
            ignored_directories={
                "__init__.py",
                "pytest_cache",
                ".git",
                "manage.py",
                "setup.py",
                "__pycache__",
                "venv",
            },
            ignored_files={"__init__.py", "manage.py", "setup.py"},
        )
        self._mock_create_file_and_directory.assert_called_once_with(
            directory=DEFAULT_REPORT_DIRECTORY,
            file_name=DEFAULT_REPORT_FILENAME,
            content="# File name: b/file1.py \n\n Points found:\nI am not able to perform the code review of this file",
        )

    def test__review_dir__when_no_files__then_return_success(self):
        self._mock_find_all_files.return_value = {}

        result = self.runner.invoke(
            self._cli.cli,
            [
                "--quick-command-id",
                "test_command",
                "--client-id",
                "test_client-id",
                "--client-secret",
                "test_client-secret",
                "review-dir",
            ],
            prog_name=APPLICATION_NAME,
        )

        self.assertEqual(EXIT_SUCCESS, result.exit_code)

        self._mock_find_all_files.assert_called_once_with(
            directory=".",
            extension=".py",
            ignored_directories={
                "__pycache__",
                "manage.py",
                ".git",
                "pytest_cache",
                "__init__.py",
                "venv",
                "setup.py",
            },
            ignored_files={"manage.py", "__init__.py", "setup.py"},
        )
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_and_directory.assert_not_called()

    def test__review_dir__when_keyboard_error__then_return_fail(self):
        self._mock_find_all_files.side_effect = KeyboardInterrupt("Stopped")

        result = self.runner.invoke(
            self._cli.cli,
            [
                "--quick-command-id",
                "test_command",
                "--client-id",
                "test_client-id",
                "--client-secret",
                "test_client-secret",
                "review-dir",
            ],
            prog_name=APPLICATION_NAME,
        )

        self.assertEqual(EXIT_FAIL, result.exit_code)

        self._mock_find_all_files.assert_called_once()
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_and_directory.assert_not_called()

    def test__review_dir__when_environment_error__then_return_fail(self):
        self._mock_find_all_files.side_effect = EnvironmentError("error")

        result = self.runner.invoke(
            self._cli.cli,
            [
                "--quick-command-id",
                "test_command",
                "--client-id",
                "test_client-id",
                "--client-secret",
                "test_client-secret",
                "review-dir",
            ],
            prog_name=APPLICATION_NAME,
        )

        self.assertEqual(EXIT_FAIL, result.exit_code)

        self._mock_find_all_files.assert_called_once()
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_and_directory.assert_not_called()

    def test__review_dir__when_integration_error__then_return_fail(self):
        self._mock_find_all_files.return_value = {
            "/root/dir2\\file_3.py": "file content",
        }

        self._mock_review_service.side_effect = IntegrationError("error 500")

        result = self.runner.invoke(
            self._cli.cli,
            [
                "--quick-command-id",
                "test_command",
                "--client-id",
                "test_client-id",
                "--client-secret",
                "test_client-secret",
                "review-dir",
            ],
            prog_name=APPLICATION_NAME,
        )

        self.assertEqual(EXIT_FAIL, result.exit_code)

        self._mock_find_all_files.assert_called_once()
        self._mock_review_service.run.assert_called_once()
        self._mock_create_file_and_directory.assert_not_called()

    def test__review_changes__when_has_changes__then_return_success(self):
        self._mock_find_all_changed_code.return_value = {
            "file1.py": (
                "index 83db48f..e312f45 100644\n"
                "--- a/file1.py\n"
                "+++ b/file1.py\n"
                "@@ -1,4 +1,4 @@\n"
                '-print("Hello world")\n'
                '+print("Hello, world!")\n'
            )
        }

        self._mock_review_service.run.return_value = {
            "b/file1.py": "Points found:\n"
            "I am not able to perform the code review of this file",
        }

        result = self.runner.invoke(
            self._cli.cli,
            [
                "--quick-command-id",
                "test_command",
                "--client-id",
                "test_client-id",
                "--client-secret",
                "test_client-secret",
                "review-changes",
            ],
            prog_name=APPLICATION_NAME,
        )

        self.assertEqual(EXIT_SUCCESS, result.exit_code)

        self._mock_review_service.run.assert_called_once()
        self._mock_find_all_changed_code.assert_called_once_with(
            repository_path=".",
            base="main",
            compare="develop",
            extension=".py",
            ignored_directories={
                "__pycache__",
                "manage.py",
                ".git",
                "pytest_cache",
                "__init__.py",
                "venv",
                "setup.py",
            },
            ignored_files={"manage.py", "__init__.py", "setup.py"},
        )
        self._mock_find_all_files.assert_not_called()
        self._mock_create_file_and_directory.assert_called_once_with(
            directory=DEFAULT_REPORT_DIRECTORY,
            file_name=DEFAULT_REPORT_FILENAME,
            content="# File name: b/file1.py \n\n Points found:\nI am not able to perform the code review of this file",
        )

    def test__review_changes__when_no_changes__then_return_success(self):
        self._mock_find_all_changed_code.return_value = {}

        result = self.runner.invoke(
            self._cli.cli,
            [
                "--quick-command-id",
                "test_command",
                "--client-id",
                "test_client-id",
                "--client-secret",
                "test_client-secret",
                "review-changes",
            ],
            prog_name=APPLICATION_NAME,
        )

        self.assertEqual(EXIT_SUCCESS, result.exit_code)

        self._mock_find_all_changed_code.assert_called_once_with(
            repository_path=".",
            base="main",
            compare="develop",
            extension=".py",
            ignored_directories={
                "__init__.py",
                "pytest_cache",
                ".git",
                "manage.py",
                "setup.py",
                "__pycache__",
                "venv",
            },
            ignored_files={"__init__.py", "manage.py", "setup.py"},
        )
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_and_directory.assert_not_called()

    def test__review_changes__when_keyboard_error__then_return_fail(self):
        self._mock_find_all_changed_code.side_effect = KeyboardInterrupt("Stopped")

        result = self.runner.invoke(
            self._cli.cli,
            [
                "--quick-command-id",
                "test_command",
                "--client-id",
                "test_client-id",
                "--client-secret",
                "test_client-secret",
                "review-changes",
            ],
            prog_name=APPLICATION_NAME,
        )

        self.assertEqual(EXIT_FAIL, result.exit_code)

        self._mock_find_all_changed_code.assert_called_once()
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_and_directory.assert_not_called()


if __name__ == "__cli__":
    unittest.main()
