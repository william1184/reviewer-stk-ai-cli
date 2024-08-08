import logging
import os
from typing import Dict

from src.utils.constants import APPLICATION_NAME
from src.utils.file_helper import create_file

logger = logging.getLogger(APPLICATION_NAME)


def create_file_with_contents(
        file_name: str, root_directory: str, content_by_name: Dict
):
    logger.info("Starting code review report creation")

    if len(content_by_name) == 0:
        raise ValueError("No content to generate report")

    try:
        separator = "\n\n---\n\n"

        contents_md = []
        for _name in content_by_name.keys():
            contents_md.append(f"# File name: {_name} \n\n {content_by_name[_name]}")

        final_content = separator.join(contents_md)

        if not os.path.exists(root_directory):
            os.makedirs(root_directory)
            logger.debug("Directory created")

        file_name = f"{root_directory}/{file_name}.md"

        create_file(file_name, final_content)

        logger.info(f"Report '{file_name}' created successfully.")

        return {"name": file_name, "content": final_content}
    except Exception:
        logger.error(f"Error creating report: {file_name}")
        raise


__all__ = ["create_file_with_contents"]
