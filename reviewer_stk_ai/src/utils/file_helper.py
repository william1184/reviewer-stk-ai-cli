import logging
import os
from typing import Set, Dict

from reviewer_stk_ai.src.utils.constants import APPLICATION_NAME

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


def create_file_and_directory(directory: str, file_name: str, content: str) -> str:
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug(f"Directory {directory} created!")

    path = directory + "/" + file_name
    create_file(file_name=path, content=content)

    return path


def create_file(file_name: str, content: str):
    logger.debug(f"Creating file: {file_name}")

    with open(file_name, "w", encoding="utf-8") as file_md:
        file_md.write(content)

    logger.debug(f"File '{file_name}' created successfully.")


def merge_tmp_files(path: str) -> str:
    separator = "\n\n---\n\n"
    contents = []
    for dirpath, dirnames, filenames in os.walk(path):
        print(dirpath)
        for file in filenames:
            with open(f"{os.path.join(dirpath, file)}", "r") as infile:
                contents.append(infile.read())

    return separator.join(contents)


__all__ = [
    "create_file",
    "create_file_and_directory",
    "find_all_files",
    "read_file",
    "create_directory",
    "merge_tmp_files",
]
