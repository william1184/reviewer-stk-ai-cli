import sys
import unittest
from unittest import TestCase
from unittest.mock import patch


class TestReportHelper(TestCase):

    def setUp(self):
        if "src.utils.report_helper" in sys.modules:
            sys.modules.pop("src.utils.report_helper")

    @patch("src.utils.file_helper.create_file")
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_generate_file_with_contents(
        self, mock_exists, mock_makedirs, mock_create_file
    ):
        # Configure the mock for `os.path.exists`
        mock_exists.return_value = False
        # Input data for the function
        filename = "report"
        directory = "/fake_dir"
        contents_by_name = {"file1.py": "File 1 content", "file2.py": "File 2 content"}

        from src.utils.report_helper import create_file_with_contents

        # Call the function being tested
        create_file_with_contents(filename, directory, contents_by_name)

        # Verifications
        mock_makedirs.assert_called_once_with(directory)
        mock_create_file.assert_called_once()

        # Verify the content passed to `create_file`
        args, kwargs = mock_create_file.call_args
        expected_filename = "/fake_dir/report.md"
        expected_final_content = (
            "# File name: file1.py \n\n File 1 content\n\n---\n\n"
            "# File name: file2.py \n\n File 2 content"
        )
        self.assertEqual(args[0], expected_filename)
        self.assertEqual(args[1], expected_final_content)

    @patch("src.utils.file_helper.create_file")
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_generate_file_with_contents__with_empty_content(
        self, mock_exists, mock_makedirs, mock_create_file
    ):
        # Configure the mock for `os.path.exists`
        mock_exists.return_value = False

        # Input data for the function
        filename = "report"
        directory = "/fake_dir"
        contents_by_name = {}

        from src.utils.report_helper import create_file_with_contents

        # Call the function being tested
        with self.assertRaises(ValueError) as ctx:
            create_file_with_contents(filename, directory, contents_by_name)

        self.assertEqual("No content to generate report", ctx.exception.args[0])

        # Verifications
        mock_makedirs.assert_not_called()
        mock_create_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
