import unittest
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from src.exceptions.integration_error import IntegrationError
from src.utils.constants import APPLICATION_NAME, EXIT_SUCCESS, EXIT_FAIL


class TestMain(TestCase):
    _mock_find_all_files = None
    _mock_find_all_changed_code = None
    _mock_create_file_with_contents = None
    _mock_review_service = None
    _main = None

    def setUp(self):
        self._mock_review_service = patch(
            "src.service.reviewer_service.ReviewerService"
        ).start()()

        self._mock_find_all_files = patch(
            "src.utils.file_helper.find_all_files"
        ).start()
        self._mock_find_all_changed_code = patch(
            "src.utils.git_helper.find_all_changed_code"
        ).start()
        self._mock_create_file_with_contents = patch(
            "src.utils.report_helper.create_file_with_contents"
        ).start()

        import main

        self._main = main

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
                          "I am not able to perform the code review of this file.",
        }

        result = self.runner.invoke(self._main.cli, [
            "--quick-command-id", "test_command", "--client-id", "test_client-id",
            "--client-secret", "test_client-secret", "review-dir"],
                                    prog_name=APPLICATION_NAME)

        self.assertEqual(EXIT_SUCCESS, result.exit_code)

        self._mock_review_service.run.assert_called_once()
        self._mock_find_all_changed_code.assert_not_called()
        self._mock_find_all_files.assert_called_once_with(
            directory='.',
            extension='.py',
            ignored_directories={'venv', 'pytest_cache', '__pycache__',
                                 '.git'},
            ignored_files={'setup.py', 'manage.py', '__init__.py'}
        )
        self._mock_create_file_with_contents.assert_called_once_with(
            file_name='report',
            root_directory='code-report',
            content_by_name={'b/file1.py': 'Points found:\nI am not able to perform the code review of this file.'})

    def test__review_dir__when_no_files__then_return_success(self):
        self._mock_find_all_files.return_value = {}

        result = self.runner.invoke(self._main.cli, [
            "--quick-command-id", "test_command", "--client-id", "test_client-id",
            "--client-secret", "test_client-secret", "review-dir"],
                                    prog_name=APPLICATION_NAME)

        self.assertEqual(EXIT_SUCCESS, result.exit_code)

        self._mock_find_all_files.assert_called_once_with(
            directory='.', extension='.py',
            ignored_directories={'.git', 'pytest_cache',
                                 'venv', '__pycache__'},
            ignored_files={'manage.py', '__init__.py',
                           'setup.py'}
        )
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_with_contents.assert_not_called()

    def test__review_dir__when_keyboard_error__then_return_fail(self):
        self._mock_find_all_files.side_effect = KeyboardInterrupt("Stopped")

        result = self.runner.invoke(self._main.cli, [
            "--quick-command-id", "test_command", "--client-id", "test_client-id",
            "--client-secret", "test_client-secret", "review-dir"],
                                    prog_name=APPLICATION_NAME)

        self.assertEqual(EXIT_FAIL, result.exit_code)

        self._mock_find_all_files.assert_called_once()
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_with_contents.assert_not_called()

    def test__review_dir__when_environment_error__then_return_fail(self):
        self._mock_find_all_files.side_effect = EnvironmentError("error")

        result = self.runner.invoke(self._main.cli, [
            "--quick-command-id", "test_command", "--client-id", "test_client-id",
            "--client-secret", "test_client-secret", "review-dir"],
                                    prog_name=APPLICATION_NAME)

        self.assertEqual(EXIT_FAIL, result.exit_code)

        self._mock_find_all_files.assert_called_once()
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_with_contents.assert_not_called()

    def test__review_dir__when_integration_error__then_return_fail(self):
        self._mock_find_all_files.side_effect = IntegrationError("error 500")

        result = self.runner.invoke(self._main.cli, [
            "--quick-command-id", "test_command", "--client-id", "test_client-id",
            "--client-secret", "test_client-secret", "review-dir"],
                                    prog_name=APPLICATION_NAME)

        self.assertEqual(EXIT_FAIL, result.exit_code)

        self._mock_find_all_files.assert_called_once()
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_with_contents.assert_not_called()

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
                          "I am not able to perform the code review of this file.",
        }

        result = self.runner.invoke(self._main.cli, [
            "--quick-command-id", "test_command", "--client-id", "test_client-id",
            "--client-secret", "test_client-secret", "review-changes"],
                                    prog_name=APPLICATION_NAME)

        self.assertEqual(EXIT_SUCCESS, result.exit_code)

        self._mock_review_service.run.assert_called_once()
        self._mock_find_all_changed_code.assert_called_once_with(repository_path='.',
                                                                 base='main',
                                                                 compare='develop',
                                                                 extension='.py',
                                                                 ignored_directories={'.git', '__pycache__',
                                                                                      'pytest_cache', 'venv'},
                                                                 ignored_files={'setup.py', 'manage.py', '__init__.py'})
        self._mock_find_all_files.assert_not_called()
        self._mock_create_file_with_contents.assert_called_once_with(
            file_name='report', root_directory='code-report',
            content_by_name={
                'b/file1.py': 'Points found:\nI am not able to perform the code review of this file.'})

    def test__review_changes__when_no_changes__then_return_success(self):
        self._mock_find_all_changed_code.return_value = {}

        result = self.runner.invoke(self._main.cli, [
            "--quick-command-id", "test_command", "--client-id", "test_client-id",
            "--client-secret", "test_client-secret", "review-changes"],
                                    prog_name=APPLICATION_NAME)

        self.assertEqual(EXIT_SUCCESS, result.exit_code)

        self._mock_find_all_changed_code.assert_called_once_with(repository_path='.',
                                                                 base='main',
                                                                 compare='develop',
                                                                 extension='.py',
                                                                 ignored_directories={'__pycache__', 'venv', '.git',
                                                                                      'pytest_cache'},
                                                                 ignored_files={'setup.py', 'manage.py',
                                                                                '__init__.py'})
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_with_contents.assert_not_called()

    def test__review_changes__when_keyboard_error__then_return_fail(self):
        self._mock_find_all_changed_code.side_effect = KeyboardInterrupt("Stopped")

        result = self.runner.invoke(self._main.cli, [
            "--quick-command-id", "test_command", "--client-id", "test_client-id",
            "--client-secret", "test_client-secret", "review-changes"],
                                    prog_name=APPLICATION_NAME)

        self.assertEqual(EXIT_FAIL, result.exit_code)

        self._mock_find_all_changed_code.assert_called_once()
        self._mock_review_service.run.assert_not_called()
        self._mock_create_file_with_contents.assert_not_called()


if __name__ == "__cli__":
    unittest.main()
