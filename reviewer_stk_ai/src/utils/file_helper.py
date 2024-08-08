import logging
import os
from typing import Set, Dict

from src.utils.constants import APPLICATION_NAME

logger = logging.getLogger(APPLICATION_NAME)


def find_all_files(
        directory: str, extension: str, ignored_directories: Set, ignored_files: Set
) -> Dict[str, str]:
    try:
        files = {}

        for dirpath, dirnames, filenames in os.walk(directory):

            # Filtering di
            # rectories to be ignored
            is_directory_ignored = False
            for ignored_dir in ignored_directories:
                if ignored_dir in dirpath:
                    is_directory_ignored = True
                    break

            if is_directory_ignored:
                continue

            for filename in filenames:
                if filename.endswith(extension) and filename not in ignored_files:
                    file_path = os.path.join(dirpath, filename)
                    files[file_path] = read_file(file_path)

        return files
    except Exception:
        logger.error(
            f"Failed to search files in directory: {directory} with extension {extension}"
        )
        raise


def read_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()

        return file_content
    except Exception:
        logger.error(f"Failed to open file {file_path}")
        raise


def create_directory(directory: str):
    try:
        logger.debug(f"Creating directory to store the report: {directory}")
        # Check if the subfolder exists, if not, create it
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.debug(f"Directory created")

        logger.debug(f"Directory already exists")
    except Exception:
        logger.error(f"Failed to create directory: {directory}")
        raise


def create_file(file_name: str, content: str):
    try:
        logger.debug(f"Creating file: {file_name}")

        with open(file_name, "w", encoding="utf-8") as file_md:
            file_md.write(content)

        logger.debug(f"File '{file_name}' created successfully.")
    except Exception:
        logger.error(f"Error creating file: {file_name}")
        raise
