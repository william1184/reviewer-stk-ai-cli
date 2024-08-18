from __future__ import annotations

import importlib.metadata
import logging
import os
import sys
from typing import Any

import click
from click import pass_context
from git import InvalidGitRepositoryError

from reviewer_stk_ai.src.models.file_review import FileReview
from reviewer_stk_ai.src.utils.constants import APPLICATION_NAME
from reviewer_stk_ai.src.utils.constants import (
    EXIT_FAIL,
    EXIT_SUCCESS,
    DEFAULT_IGNORED_DIRECTORIES,
    DEFAULT_EXTENSION,
    DEFAULT_REPORT_DIRECTORY,
    DEFAULT_REPORT_FILENAME,
    DEFAULT_DIRECTORY,
    DEFAULT_IGNORED_FILES,
)
from reviewer_stk_ai.src.utils.file_helper import (
    create_file_and_directory,
    find_all_files,
)
from reviewer_stk_ai.src.utils.git_helper import find_all_changed_code
from reviewer_stk_ai.src.utils.report_helper import merge_contents

version = importlib.metadata.version(APPLICATION_NAME)

CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())

LOG = logging.getLogger(APPLICATION_NAME)


def common_auth_stk_options(function):
    function = click.option(
        "--https-proxy",
        type=click.STRING,
        envvar="HTTPS_PROXY",
        help="HTTPS proxy for requests.",
        metavar="<string>",
    )(function)

    function = click.option(
        "--http-proxy",
        type=click.STRING,
        envvar="HTTP_PROXY",
        help="HTTP proxy for requests.",
        metavar="<string>",
    )(function)

    function = click.option(
        "--retry-timeout",
        type=click.STRING,
        envvar="CR_STK_AI_RETRY_TIMEOUT",
        default="10",
        help="Wait time in seconds between response checks.",
        metavar="<int>",
    )(function)

    function = click.option(
        "--retry-max-attempts",
        type=click.STRING,
        envvar="CR_STK_AI_MAX_ATTEMPTS",
        default="10",
        help="Number of retries to wait for the callback",
        metavar="<int>",
    )(function)

    function = click.option(
        "--realm",
        type=click.STRING,
        envvar="CR_STK_AI_REALM",
        default="zup",
        help="Domain where the token will be generated.",
        metavar="<string>",
    )(function)

    function = click.option(
        "--host-stk-ai",
        type=click.STRING,
        envvar="CR_STK_AI_HOST",
        default="https://genai-code-buddy-api.stackspot.com",
        help="Host of the stk ai api.",
        metavar="<string>",
    )(function)

    function = click.option(
        "--host-token-stk-ai",
        type=click.STRING,
        envvar="CR_STK_AI_HOST_TOKEN",
        default="https://idm.stackspot.com",
        help="Host of the token api.",
        metavar="<string>",
    )(function)

    function = click.option(
        "--client-secret",
        type=click.STRING,
        envvar="CR_STK_AI_CLIENT_SECRET",
        help="Client secret generated on the StackSpot AI platform",
        required=True,
        metavar="<string>",
    )(function)

    function = click.option(
        "--client-id",
        type=click.STRING,
        envvar="CR_STK_AI_CLIENT_ID",
        help="Client ID generated on the StackSpot AI platform",
        required=True,
        metavar="<string>",
    )(function)

    function = click.option(
        "--quick-command-id",
        type=click.STRING,
        envvar="CR_STK_AI_ID_QUICK_COMMAND",
        help="Remote quick command identifier on the STK AI portal",
        required=True,
        metavar="<string>",
    )(function)

    return function


def common_param_options(function):
    function = click.option(
        "--report-filename",
        type=click.STRING,
        default=DEFAULT_REPORT_FILENAME,
        help="Report file name",
        metavar="<string>",
    )(function)

    function = click.option(
        "--report-directory",
        type=click.STRING,
        default=DEFAULT_REPORT_DIRECTORY,
        help="Directory where the report will be saved",
        metavar="<string>",
    )(function)

    function = click.option(
        "--ignored-directories",
        type=click.STRING,
        multiple=True,
        default=DEFAULT_IGNORED_DIRECTORIES,
        help="List of directories to ignore",
    )(function)

    function = click.option(
        "--ignored-files",
        type=click.STRING,
        multiple=True,
        default=DEFAULT_IGNORED_FILES,
        help="List of files to ignore",
    )(function)

    function = click.option(
        "--extension",
        type=click.STRING,
        default=DEFAULT_EXTENSION,
        help="File extension to be reviewed",
        metavar="<string>",
    )(function)

    function = click.option(
        "--directory",
        type=click.STRING,
        default=DEFAULT_DIRECTORY,
        help="Path to the directory where the files are located",
    )(function)

    return function


@click.group(invoke_without_command=True)
@common_auth_stk_options
@common_param_options
@click.version_option(version, prog_name=APPLICATION_NAME)
@click.option("--debug/--no-debug", default=False)
@pass_context
def cli(
    ctx,
    quick_command_id,
    client_id,
    client_secret,
    host_stk_ai,
    host_token_stk_ai,
    realm,
    retry_max_attempts,
    retry_timeout,
    http_proxy,
    https_proxy,
    directory,
    extension,
    ignored_files,
    ignored_directories,
    report_directory,
    report_filename,
    debug,
) -> Any:
    from reviewer_stk_ai.src.service.stk_token_service import StkTokenService
    from reviewer_stk_ai.src.service.stk_execution_service import StkExecutionService
    from reviewer_stk_ai.src.service.stk_callback_service import StkCallbackService
    from reviewer_stk_ai.src.service.reviewer_service import ReviewerService

    ctx.ensure_object(dict)

    logging_level = logging.DEBUG if debug else logging.INFO
    if "LOG_LEVEL" in os.environ:
        logging_level = logging.getLevelNamesMapping().get(
            os.environ["LOG_LEVEL"].upper()
        )

    LOG.setLevel(logging_level)

    if logging.DEBUG != logging_level:
        sys.tracebacklimit = 0

    from reviewer_stk_ai.src.config.env_config import EnvConfig

    if logging.DEBUG == logging_level:
        click.echo(f"Quick command id: {quick_command_id}")
        click.echo(f"Realm: {realm}")
        click.echo(f"Directory: {directory}")
        click.echo(f"File extension: {extension}")
        click.echo(f"Ignored directories: {ignored_directories}")
        click.echo(f"Ignored files: {ignored_files}")
        click.echo(f"Report directory: {report_directory}")
        click.echo(f"Report filename: {report_filename}")

    LOG.debug(
        "Loading config...",
        extra={
            "properties": {
                "client_id",
                client_id[:4],
                "client_secret",
                client_secret[:4],
                "host_stk_ai",
                host_stk_ai,
                "host_token_stk_ai",
                host_token_stk_ai,
                "retry_timeout",
                retry_timeout,
                "retry_max_attempts",
                retry_max_attempts,
                "http_proxy",
                http_proxy,
                "https_proxy",
                https_proxy,
            }
        },
    )
    ctx.obj["params"] = ctx.params
    ctx.obj["config"] = EnvConfig(args=ctx.params)

    stk_token_service = StkTokenService(env_config=ctx.obj["config"])

    stk_execution_service = StkExecutionService(
        env_config=ctx.obj["config"], stk_token_service=stk_token_service
    )

    stk_callback_service = StkCallbackService(
        env_config=ctx.obj["config"], stk_token_service=stk_token_service
    )

    ctx.obj["reviewer_service"] = ReviewerService(
        stk_execution_service=stk_execution_service,
        stk_callback_service=stk_callback_service,
    )

    if ctx.invoked_subcommand is None:
        ctx.invoke(review_dir)


def run(ctx, params, files):
    if len(files) == 0:
        click.echo("No items to analyze!")
        return EXIT_SUCCESS

    files_reviews = FileReview.list_from_dict(files=files)

    click.echo("Reviewing files...")
    content_by_name = ctx.obj["reviewer_service"].run(file_reviews=files_reviews)

    click.echo("Merging report files...")
    content = merge_contents(content_by_name=content_by_name)

    click.echo("Creating report file...")
    file_name_with_extension = params["report_filename"]
    create_file_and_directory(
        directory=params["report_directory"],
        file_name=file_name_with_extension,
        content=content,
    )

    file_path = params["report_directory"] + "/" + file_name_with_extension
    click.echo(f"Report file created on {click.format_filename(file_path)}.")

    return EXIT_SUCCESS


@cli.command(
    context_settings=CONTEXT_SETTINGS, short_help="Send the changes for reviewing."
)
@click.option(
    "--base-branch",
    type=click.STRING,
    default="main",
    help="The Branch that should be the base for diff",
    metavar="<string>",
)
@click.option(
    "--compare-branch",
    type=click.STRING,
    default="develop",
    help="The Branch should be compared to base for diff",
    metavar="<string>",
)
@click.pass_context
def review_changes(ctx, base_branch, compare_branch):
    params = ctx.obj["params"]
    try:
        click.echo(f"Finding files changed files {base_branch} > {compare_branch}.")

        files = find_all_changed_code(
            repository_path=params["directory"],
            base=base_branch,
            compare=compare_branch,
            extension=params["extension"],
            ignored_directories=convert_ignored_directories(params),
            ignored_files=convert_ignored_files(params),
        )

        click.echo(f"Were found {len(files)} modified files...")

        return run(ctx, params, files)
    except InvalidGitRepositoryError as e:
        click.echo("Current repository is not a git repository!")

    return EXIT_FAIL


@cli.command(
    context_settings=CONTEXT_SETTINGS, short_help="Send all files on dir for reviewing."
)
@click.pass_context
def review_dir(ctx):
    params = ctx.obj["params"]
    click.echo(f"Finding files by directory: \"{params['directory']}\"")

    files = find_all_files(
        directory=params["directory"],
        extension=params["extension"],
        ignored_directories=convert_ignored_directories(params),
        ignored_files=convert_ignored_files(params),
    )

    click.echo(f"Were found {len(files)} files in this directory...")

    return run(ctx, params, files)


def convert_ignored_files(params):
    ignored_files_set = set(params["ignored_files"])
    if "py" in params["extension"]:
        ignored_files_set.update(DEFAULT_IGNORED_FILES)

    return ignored_files_set


def convert_ignored_directories(params):
    ignored_directories_set = set(params["ignored_files"])
    if "py" in params["extension"]:
        ignored_directories_set.update(DEFAULT_IGNORED_DIRECTORIES)

    return ignored_directories_set
