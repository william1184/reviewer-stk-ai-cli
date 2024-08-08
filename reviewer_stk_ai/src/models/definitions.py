from typing import Dict, Set

from src.utils.constants import DEFAULT_IGNORED_FILES, DEFAULT_IGNORED_DIRECTORIES


class Definitions:
    # input data
    _directory: str = None
    _extension: str = None
    _ignored_directories: Set[str] = None
    _ignored_files: Set[str] = None

    # output data
    _report_directory: str
    _report_filename: str

    def __init__(self, args: Dict):
        self._directory = args['directory']
        self._extension = args['extension']

        self._report_directory = args['report_directory']
        self._report_filename = args['report_filename']

        self._ignored_directories = set()
        self._ignored_files = set()
        self._ignored_files = set(args['ignored_files'])
        self._ignored_files.update(DEFAULT_IGNORED_FILES)

        self._ignored_directories = set(args['ignored_directories'])
        self._ignored_directories.update(DEFAULT_IGNORED_DIRECTORIES)

    # Getters
    def get_directory(self) -> str:
        return self._directory

    def get_extension(self) -> str:
        return self._extension

    def get_ignored_files(self) -> Set[str]:
        return self._ignored_files

    def get_ignored_directories(self) -> Set[str]:
        return self._ignored_directories

    def get_report_directory(self) -> str:
        return self._report_directory

    def get_report_filename(self) -> str:
        return self._report_filename
