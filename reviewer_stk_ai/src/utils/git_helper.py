from typing import Set, Dict

import git


def get_changed_files(
    repository: git.Repo,
    base: str,
    compare: str,
    extension: str,
    ignored_directories: Set,
    ignored_files: Set,
):
    """
    Returns a list of files that have changed between two branches.
    """
    changed_files = []
    diff = repository.git.diff(f"{base}..{compare}", name_only=True)
    for file in diff.split("\n"):
        path = file.split("/")
        file_name: str = path[-1]

        if not file_name.endswith(extension):
            continue

        is_exist_directory = False
        for _ignored_directory in ignored_directories:
            if _ignored_directory in path:
                is_exist_directory = True
                break

        if is_exist_directory or (file_name in ignored_files):
            continue

        changed_files.append(file)

    return changed_files


def get_file_diffs(repository: git.Repo, base: str, compare: str):
    """
    Returns a dictionary with file names as keys and their diffs as values.
    """
    file_diffs = {}
    diffs = repository.git.diff(f"{base}..{compare}", unified=0)
    diff_entries = diffs.split("diff --git ")
    for entry in diff_entries[1:]:
        lines = entry.split("\n")
        file_name = lines[0].split(" ")[-1].replace("b/", "")
        diff = "\n".join(lines[1:])
        file_diffs[file_name] = diff
    return file_diffs


def find_all_changed_code(
    repository_path: str,
    base: str,
    compare: str,
    extension: str,
    ignored_directories: Set,
    ignored_files: Set,
) -> Dict[str, str]:
    """
    Returns a dictionary with the files that changed and the altered code.
    """
    repository = git.Repo(repository_path)

    changed_files = get_changed_files(
        repository, base, compare, extension, ignored_directories, ignored_files
    )

    changed_codes = {}

    if changed_files:
        file_diffs = get_file_diffs(repository, base, compare)
        changed_codes = {file: file_diffs[file] for file in changed_files}

    return changed_codes
