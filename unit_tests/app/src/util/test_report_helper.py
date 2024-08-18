import sys
import unittest
from unittest import TestCase


class TestReportHelper(TestCase):

    def setUp(self):
        if "src.utils.report_helper" in sys.modules:
            sys.modules.pop("src.utils.report_helper")

    def test__merge_contents__when_has_contents__return_content(self):
        contents_by_name = {"file1.py": "File 1 content", "file2.py": "File 2 content"}

        from src.utils.report_helper import merge_contents

        content_merged = merge_contents(contents_by_name)

        expected_final_content = (
            "# File name: file1.py \n\n File 1 content\n\n---\n\n"
            "# File name: file2.py \n\n File 2 content"
        )
        self.assertEqual(content_merged, expected_final_content)

    def test__merge_contents__when_no_contents__return_content(self):
        contents_by_name = {}

        from src.utils.report_helper import merge_contents

        with self.assertRaises(ValueError) as ctx:
            merge_contents(contents_by_name)

        self.assertEqual("No content to generate report", ctx.exception.args[0])


if __name__ == "__main__":
    unittest.main()
