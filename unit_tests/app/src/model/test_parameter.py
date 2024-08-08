import unittest
from unittest import TestCase

from src.models.definitions import Definitions


class TestDefinitions(TestCase):

    def test__case__all_properties_filled__then__return_success(
            self,
    ):
        args = {
            "directory": ".",
            "extension": ".py",
            "ignored_files": ["file_1", "file_2"],
            "ignored_directories": ["directory"],
            "report_directory": "code-review",
            "report_filename": "code-review-report"
        }

        param = Definitions(args=args)

        self.assertEqual(".", param.get_directory())
        self.assertEqual(".py", param.get_extension())
        self.assertEqual(
            {"file_2", "file_1", "__init__.py", "setup.py", "manage.py"},
            param.get_ignored_files(),
        )
        self.assertEqual(
            {"directory", "venv", ".git", "pytest_cache", "__pycache__"},
            param.get_ignored_directories(),
        )
        self.assertEqual("code-review", param.get_report_directory())
        self.assertEqual("code-review-report", param.get_report_filename())

    def test__case__all_properties_filled_with_ignore_files_unfilled__then__return_success(self):
        args = {
            "directory": ".",
            "extension": ".py",
            "ignored_files": [],
            "ignored_directories": ["directory"],
            "report_directory": "code-review",
            "report_filename": "code-review-report"
        }

        param = Definitions(args=args)

        self.assertEqual(".", param.get_directory())
        self.assertEqual(".py", param.get_extension())
        self.assertEqual(
            {"__init__.py", "setup.py", "manage.py"}, param.get_ignored_files()
        )
        self.assertEqual(
            {"directory", "venv", ".git", "pytest_cache", "__pycache__"},
            param.get_ignored_directories(),
        )
        self.assertEqual("code-review", param.get_report_directory())
        self.assertEqual("code-review-report", param.get_report_filename())

    def test__case__all_properties_filled_with_ignore_directories_unfilled__then__return_success(self):
        args = {
            "directory": ".",
            "extension": ".py",
            "ignored_files": ["file_1", "file_2"],
            "ignored_directories": [],
            "report_directory": "code-review",
            "report_filename": "code-review-report"
        }

        param = Definitions(args=args)

        self.assertEqual(".", param.get_directory())
        self.assertEqual(".py", param.get_extension())
        self.assertEqual(
            {"file_2", "file_1", "__init__.py", "setup.py", "manage.py"}, param.get_ignored_files()
        )
        self.assertEqual(
            {"venv", ".git", "pytest_cache", "__pycache__"},
            param.get_ignored_directories(),
        )
        self.assertEqual("code-review", param.get_report_directory())
        self.assertEqual("code-review-report", param.get_report_filename())


if __name__ == "__main__":
    unittest.main()
