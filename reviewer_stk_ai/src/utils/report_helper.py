import logging

from reviewer_stk_ai.src.utils.constants import APPLICATION_NAME, TEMP_PATH
from reviewer_stk_ai.src.utils.file_helper import (
    create_file_and_directory,
    merge_tmp_files,
)

logger = logging.getLogger(APPLICATION_NAME)


def generate_report(directory: str, file_name: str) -> None:
    content = merge_tmp_files(TEMP_PATH)

    if len(content.strip()) == 0:
        raise ValueError(f"No content to generate report, at {TEMP_PATH}")

    create_file_and_directory(directory=directory, file_name=file_name, content=content)


__all__ = ["generate_report"]
