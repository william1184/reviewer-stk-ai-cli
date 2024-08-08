import unittest
from unittest import TestCase, mock
from unittest.mock import mock_open, patch


class TestFileHelper(TestCase):

    @mock.patch("os.walk")
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_find_all_files_no_ignored_files_or_directories_with_py_extension_should_return_expected_paths(
            self, mock_read_file, mock_os_walk
    ):
        # arrange
        expected_paths = {
            "/root/dir1\\file_2.py": "file content",
            "/root/dir2\\file_3.py": "file content",
            "/root\\file.py": "file content",
            "/root\\file_1.py": "file content",
        }

        mock_os_walk.return_value = [
            ("/root", ["dir1", "dir2"], ["file.py", "file_1.py"]),
            ("/root/dir1", [], ["file_2.py"]),
            ("/root/dir2", [], ["file_3.py", "file.txt"]),
        ]

        # act
        from src.utils.file_helper import find_all_files

        paths = find_all_files(
            directory=".",
            extension=".py",
            ignored_directories=set(),
            ignored_files=set(),
            
        )

        # assert
        self.assertEqual(paths, expected_paths)

    @mock.patch("os.walk")
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_find_all_files_with_ignored_file_and_directory_with_py_extension_should_return_expected_paths(
            self, mock_read_file, mock_os_walk
    ):
        # arrange
        expected_paths = {
            "/root\\file.py": "file content",
            "/root\\file_1.py": "file content",
        }

        mock_os_walk.return_value = [
            ("/root", ["dir1", "dir2"], ["file.py", "file_1.py"]),
            ("/root/dir1", [], ["file_2.py"]),
            ("/root/dir2", [], ["file_3.py", "file.txt"]),
        ]

        # act
        from src.utils.file_helper import find_all_files

        paths = find_all_files(
            directory=".",
            extension=".py",
            ignored_directories={"dir1"},
            ignored_files={"file_3.py"},
        )

        # assert
        self.assertEqual(paths, expected_paths)

    @mock.patch("os.walk")
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_find_all_files_with_ignored_files_no_ignored_directories_with_py_extension_should_return_expected_paths(
            self, mock_read_file, mock_os_walk
    ):
        # arrange
        expected_paths = {
            "/root/dir1\\file_2.py": "file content",
            "/root\\file.py": "file content",
            "/root\\file_1.py": "file content",
        }

        mock_os_walk.return_value = [
            ("/root", ["dir1", "dir2"], ["file.py", "file_1.py"]),
            ("/root/dir1", [], ["file_2.py"]),
            ("/root/dir2", [], ["file_3.py", "file.txt"]),
        ]

        # act
        from src.utils.file_helper import find_all_files

        paths = find_all_files(
            directory=".",
            extension=".py",
            ignored_directories=set(),
            ignored_files={"file_3.py"}
        )

        # assert
        self.assertEqual(paths, expected_paths)

    @mock.patch("os.walk")
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_find_all_files_when_ignore_directory_and_extension_eq_py_return_expected_paths(
            self, mock_read_file, mock_os_walk
    ):
        # arrange
        expected_paths = {
            "/root/dir2\\file_3.py": "file content",
            "/root\\file.py": "file content",
            "/root\\file_1.py": "file content",
        }

        mock_os_walk.return_value = [
            ("/root", ["dir1", "dir2"], ["file.py", "file_1.py"]),
            ("/root/dir1", [], ["file_2.py"]),
            ("/root/dir2", [], ["file_3.py", "file.txt"]),
        ]

        # act
        from src.utils.file_helper import find_all_files

        paths = find_all_files(
            directory=".",
            extension=".py",
            ignored_directories={"dir1"},
            ignored_files=set(),
            
        )

        # assert
        self.assertEqual(paths, expected_paths)

    @mock.patch("os.walk")
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_find_all_files_no_ignored_files_or_directories_with_txt_extension_should_return_expected_paths(
            self, mock_read_file, mock_os_walk
    ):
        # arrange
        expected_paths = {"/root/dir2\\file.txt": "file content"}

        mock_os_walk.return_value = [
            ("/root", ["dir1", "dir2"], ["file.py", "file_1.py"]),
            ("/root/dir1", [], ["file_2.py"]),
            ("/root/dir2", [], ["file_3.py", "file.txt"]),
        ]

        # act
        from src.utils.file_helper import find_all_files

        paths = find_all_files(
            directory=".",
            extension=".txt",
            ignored_directories=set(".venv"),
            ignored_files=set("__init__"),
            
        )

        # assert
        self.assertEqual(paths, expected_paths)

    @patch("os.walk", side_effect=Exception("Error walking through directory"))
    def test_find_all_files_failure(self, mock_os_walk):
        directory = "/test/dir"
        extension = ".txt"
        ignored_directories = {"/test/dir/ignored"}
        ignored_files = {"file2.md"}

        from src.utils.file_helper import find_all_files

        with self.assertRaises(Exception):
            find_all_files(directory, extension, ignored_directories, ignored_files, )

    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_read_file_success(self, mock_file):
        file_path = "fake/path/file.txt"

        from src.utils.file_helper import read_file

        content = read_file(file_path)
        self.assertEqual(content, "file content")
        mock_file.assert_called_once_with(file_path, "r", encoding="utf-8")

    @patch("builtins.open", side_effect=Exception("Error opening file"))
    def test_read_file_failure(self, mock_file):
        file_path = "fake/path/file.txt"

        from src.utils.file_helper import read_file

        with self.assertRaises(Exception):
            read_file(file_path)
        mock_file.assert_called_once_with(file_path, "r", encoding="utf-8")

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_directory_when_not_exists(self, mock_makedirs, mock_path_exists):
        # Configure mocks
        mock_path_exists.return_value = False

        directory = "some/fake/directory"

        from src.utils.file_helper import create_directory

        # Call the function
        create_directory(directory)

        # Verify if the correct methods were called
        mock_path_exists.assert_called_once_with(directory)
        mock_makedirs.assert_called_once_with(directory)

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_directory_when_exists(self, mock_makedirs, mock_path_exists):
        # Configure mocks
        mock_path_exists.return_value = True

        directory = "some/fake/directory"

        from src.utils.file_helper import create_directory

        # Call the function
        create_directory(directory)

        # Verify if the correct methods were called
        mock_path_exists.assert_called_once_with(directory)
        mock_makedirs.assert_not_called()

    @patch("os.path.exists", side_effect=Exception("Some error"))
    def test_create_directory_failure(self, mock_path_exists):
        directory = "some/fake/directory"

        from src.utils.file_helper import create_directory

        # Verify if the exception is raised
        with self.assertRaises(Exception):
            create_directory(directory)

        # Verify if the correct methods were called
        mock_path_exists.assert_called_once_with(directory)

    @patch("builtins.open", new_callable=mock_open)
    def test_create_file_success(self, mock_file):
        file_name = "fake_file.md"
        content = "This is the file content."

        from src.utils.file_helper import create_file

        create_file(file_name, content)

        # Verify if the file was opened correctly
        mock_file.assert_called_once_with(file_name, "w", encoding="utf-8")

        # Verify if the content was written to the file
        mock_file().write.assert_called_once_with(content)

    @patch("builtins.open", side_effect=Exception("Error creating file"))
    def test_create_file_failure(self, mock_file):
        file_name = "fake_file.md"
        content = "This is the file content."

        from src.utils.file_helper import create_file

        with self.assertRaises(Exception):
            create_file(file_name, content)

        # Verify if the file was attempted to be opened correctly
        mock_file.assert_called_once_with(file_name, "w", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
