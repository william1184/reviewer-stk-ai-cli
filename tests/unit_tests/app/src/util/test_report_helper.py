import sys
import unittest
from unittest import TestCase
from unittest.mock import patch


class TestReportHelper(TestCase):

    def setUp(self):
        if "reviewer_stk_ai.src.utils.report_helper" in sys.modules:
            sys.modules.pop("reviewer_stk_ai.src.utils.report_helper")

    @patch("reviewer_stk_ai.src.utils.file_helper.merge_tmp_files")
    @patch("reviewer_stk_ai.src.utils.file_helper.create_file_and_directory")
    def test__generate_report__when_has_tmp_files__then_create_a_report(
        self, create_file_and_directory, merge_tmp_files
    ):
        merge_tmp_files.return_value = "file_merged\n\n\nfile_merged\n\n\n"

        from reviewer_stk_ai.src.utils.report_helper import generate_report

        generate_report(directory="./", file_name="report.md")

        create_file_and_directory.assert_called_with(
            directory="./",
            file_name="report.md",
            content="file_merged\n\n\nfile_merged\n\n\n",
        )

    @patch("reviewer_stk_ai.src.utils.file_helper.merge_tmp_files")
    @patch("reviewer_stk_ai.src.utils.file_helper.create_file_and_directory")
    def test__generate_report__when_has_not_tmp_files__then_return_exception(
        self, create_file_and_directory, merge_tmp_files
    ):
        merge_tmp_files.return_value = ""

        from reviewer_stk_ai.src.utils.report_helper import generate_report

        with self.assertRaises(ValueError) as ctx:
            generate_report(directory="./", file_name="report.md")

        self.assertEqual(
            "No content to generate report, at ./tmp", ctx.exception.args[0]
        )

        create_file_and_directory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
