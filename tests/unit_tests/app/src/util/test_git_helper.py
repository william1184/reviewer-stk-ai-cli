import sys
import unittest
from unittest.mock import patch


class TestGitHelper(unittest.TestCase):
    def setUp(self):
        if "git" in sys.modules:
            del sys.modules["git"]

        if "src.utils.git_helper" in sys.modules:
            del sys.modules["src.utils.git_helper"]

    @patch("git.Repo")
    def test__get_changed_files_when_without_ignored__success(self, mock_repo):
        from src.utils.git_helper import get_changed_files

        # Set up the mock for the git diff command
        mock_repo().git.diff.return_value = "file1.py\nfile2.py\n"

        # Call the method and verify the result
        changed_files = get_changed_files(
            mock_repo(), "main", "feature-branch", "py", set(), set()
        )
        expected_files = ["file1.py", "file2.py"]

        self.assertEqual(changed_files, expected_files)

    @patch("git.Repo")
    def test__get_changed_files_when_different_extension__return_one_file(
        self, mock_repo
    ):
        from src.utils.git_helper import get_changed_files

        # Set up the mock for the git diff command
        mock_repo().git.diff.return_value = "dir/a/file1.java\ndir/b/file2.py\n"

        # Call the method and verify the result
        changed_files = get_changed_files(
            mock_repo(),
            "main",
            "feature-branch",
            "java",
            ignored_directories=set(),
            ignored_files=set(),
        )
        expected_files = ["dir/a/file1.java"]

        self.assertTrue(changed_files, expected_files)

    @patch("git.Repo")
    def test__get_changed_files_when_with_ignored_file__return_one_file(
        self, mock_repo
    ):
        from src.utils.git_helper import get_changed_files

        # Set up the mock for the git diff command
        mock_repo().git.diff.return_value = "dir/a/file1.py\ndir/b/file2.py\n"

        # Call the method and verify the result
        changed_files = get_changed_files(
            mock_repo(),
            "main",
            "feature-branch",
            "py",
            ignored_directories=set(),
            ignored_files=set(["file2.py"]),
        )
        expected_files = ["dir/a/file1.py"]

        self.assertEqual(changed_files, expected_files)

    @patch("git.Repo")
    def test__get_changed_files_when_with_ignored_dir__return_one_file(self, mock_repo):
        from src.utils.git_helper import get_changed_files

        # Set up the mock for the git diff command
        mock_repo().git.diff.return_value = "dir/a/file1.py\ndir/b/file2.py\n"

        # Call the method and verify the result
        changed_files = get_changed_files(
            mock_repo(),
            "main",
            "feature-branch",
            "py",
            ignored_directories=set(["a"]),
            ignored_files=set(),
        )
        expected_files = ["dir/b/file2.py"]

        self.assertEqual(changed_files, expected_files)

    @patch("git.Repo")
    def test__get_changed_files_when_all_files_ignored__return_empty(self, mock_repo):
        from src.utils.git_helper import get_changed_files

        # Set up the mock for the git diff command
        mock_repo().git.diff.return_value = (
            "dir/a/file1.py\ndir/b/file2.py\ndir/c/file2.md\n"
        )

        # Call the method and verify the result
        changed_files = get_changed_files(
            mock_repo(),
            "main",
            "feature-branch",
            "py",
            ignored_directories=set(["a"]),
            ignored_files=set(["file2.py"]),
        )
        expected_files = []

        self.assertEqual(changed_files, expected_files)

    @patch("git.Repo")
    def test__get_file_diffs__success(self, mock_repo):
        from src.utils.git_helper import get_file_diffs

        # Set up the mock for the git diff command
        mock_repo().git.diff.return_value = (
            "diff --git a/file1.py b/file1.py\n"
            "index 83db48f..e312f45 100644\n"
            "--- a/file1.py\n"
            "+++ b/file1.py\n"
            "@@ -1,4 +1,4 @@\n"
            '-print("Hello world")\n'
            '+print("Hello, world!")\n'
        )

        # Call the method and verify the result
        file_diffs = get_file_diffs(mock_repo(), "main", "feature-branch")
        self.assertEqual(
            file_diffs,
            {
                "file1.py": (
                    "index 83db48f..e312f45 100644\n"
                    "--- a/file1.py\n"
                    "+++ b/file1.py\n"
                    "@@ -1,4 +1,4 @@\n"
                    '-print("Hello world")\n'
                    '+print("Hello, world!")\n'
                )
            },
        )

    @patch("git.Repo")
    def test__find_all_changed_code__sucesss(self, mock_repo):
        from src.utils.git_helper import find_all_changed_code

        # Set up the mock for the git diff commands
        mock_repo().git.diff.side_effect = [
            "file1.py\nfile2.py\n",
            (
                "diff --git a/file1.py b/file1.py\n"
                "index 83db48f..e312f45 100644\n"
                "--- a/file1.py\n"
                "+++ b/file1.py\n"
                "@@ -1,4 +1,4 @@\n"
                '-print("Hello world")\n'
                '+print("Hello, world!")\n'
                "diff --git a/file2.py b/file2.py\n"
                "index 83db48f..e312f45 100644\n"
                "--- a/file2.py\n"
                "+++ b/file2.py\n"
                "@@ -1,4 +1,4 @@\n"
                '-print("Goodbye world")\n'
                '+print("Goodbye, world!")\n'
            ),
        ]

        # Call the method and verify the result
        changed_code = find_all_changed_code(
            "/fake/repo/path", "main", "feature-branch", "py", set(), set()
        )

        self.assertEqual(
            changed_code,
            {
                "file1.py": (
                    "index 83db48f..e312f45 100644\n"
                    "--- a/file1.py\n"
                    "+++ b/file1.py\n"
                    "@@ -1,4 +1,4 @@\n"
                    '-print("Hello world")\n'
                    '+print("Hello, world!")\n'
                ),
                "file2.py": (
                    "index 83db48f..e312f45 100644\n"
                    "--- a/file2.py\n"
                    "+++ b/file2.py\n"
                    "@@ -1,4 +1,4 @@\n"
                    '-print("Goodbye world")\n'
                    '+print("Goodbye, world!")\n'
                ),
            },
        )


if __name__ == "__main__":
    unittest.main()
