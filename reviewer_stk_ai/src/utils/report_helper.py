import logging
import os
from typing import Dict

from reviewer_stk_ai.src.utils.constants import APPLICATION_NAME
from reviewer_stk_ai.src.utils.file_helper import create_file

logger = logging.getLogger(APPLICATION_NAME)


def merge_contents(content_by_name: Dict) -> str:
    if len(content_by_name) == 0:
        raise ValueError("No content to generate report")

    separator = "\n\n---\n\n"

    contents_md = []
    for _name in content_by_name.keys():
        contents_md.append(f"# File name: {_name} \n\n {content_by_name[_name]}")

    return separator.join(contents_md)


__all__ = ["merge_contents"]
