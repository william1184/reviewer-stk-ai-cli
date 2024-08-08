from typing import Dict


def get_required_properties(args: Dict, property_name: str):
    content = None
    if property_name in args:
        content = args[property_name]

    if isinstance(content, int):
        return content

    if isinstance(content, str):
        if len(content.strip()) == 0:
            content = None

    if content is None:
        raise EnvironmentError(f"The property {property_name} is required")

    return content
