from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import Any

import click
import colorlog
from click import pass_context

from src.models.file_review import FileReview
from src.utils.constants import APPLICATION_NAME, EXIT_SUCCESS
from src.utils.constants import (
    DEFAULT_EXTENSION,
    DEFAULT_REPORT_DIRECTORY,
    DEFAULT_REPORT_FILENAME,
    DEFAULT_DIRECTORY,
)
from src.utils.file_helper import find_all_files
from src.utils.git_helper import find_all_changed_code


def setup_log():
    logger = logging.getLogger(APPLICATION_NAME)

    logging_level = logging.INFO
    if "LOG_LEVEL" in os.environ:
        logging_level = logging.getLevelNamesMapping().get(os.environ["LOG_LEVEL"].upper())

    logger.setLevel(logging_level)

    if logging.DEBUG != logging_level:
        sys.tracebacklimit = 0

    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


LOG = setup_log()


def common_auth_stk_options(function):
    function = click.option(
        '--https-proxy',
        type=click.STRING,
        default=lambda: os.environ.get("HTTPS_PROXY", ""),
        help='HTTPS proxy for requests.'
    )(function)

    function = click.option(
        '--http-proxy',
        type=click.STRING,
        default=lambda: os.environ.get("HTTP_PROXY", ""),
        help='HTTP proxy for requests.'
    )(function)

    function = click.option(
        '--retry-timeout',
        type=click.STRING,
        default=lambda: os.environ.get("CR_STK_AI_RETRY_TIMEOUT", "10"),
        help='Wait time in seconds between response checks.'
    )(function)

    function = click.option(
        '--retry-max-attempts',
        type=click.STRING,
        default=lambda: os.environ.get("CR_STK_AI_MAX_ATTEMPTS", "10"),
        help='Number of retries to wait for the callback'
    )(function)

    function = click.option(
        '--realm',
        type=click.STRING,
        default=lambda: os.environ.get("CR_STK_AI_REALM", "zup"),
        help='Domain where the token will be generated.'
    )(function)

    function = click.option(
        '--host-stk-ai',
        type=click.STRING,
        default=lambda: os.environ.get("HOST_STK_AI", "https://genai-code-buddy-api.stackspot.com"),
        help='Host of the stk ai api.'
    )(function)

    function = click.option(
        '--host-token-stk-ai',
        type=click.STRING,
        default=lambda: os.environ.get("HOST_TOKEN_STK_AI", "https://idm.stackspot.com"),
        help='Host of the token api.'
    )(function)

    function = click.option(
        '--client-secret',
        type=click.STRING,
        default=lambda: os.environ.get("CR_STK_AI_CLIENT_SECRET", ""),
        help='Client secret generated on the StackSpot AI platform'
    )(function)

    function = click.option(
        '--client-id',
        type=click.STRING,
        default=lambda: os.environ.get("CR_STK_AI_CLIENT_ID", ""),
        help='Client ID generated on the StackSpot AI platform'
    )(function)

    function = click.option(
        '--quick-command-id',
        type=click.STRING,
        default=lambda: os.environ.get("CR_STK_AI_ID_QUICK_COMMAND", ""),
        help='Remote quick command identifier on the STK AI portal'
    )(function)

    return function


def common_param_options(function):
    function = click.option(
        '--limit',
        type=click.STRING,
        default=lambda: os.environ.get("CR_STK_AI_LIMIT", ""),
        help='Limit of files/changes to send to ai'
    )(function)
    function = click.option(
        '--report-filename',
        type=click.STRING,
        default=DEFAULT_REPORT_FILENAME,
        help='Report file name'
    )(function)

    function = click.option(
        '--report-directory',
        type=click.STRING,
        default=DEFAULT_REPORT_DIRECTORY,
        help='Directory where the report will be saved'
    )(function)

    function = click.option(
        '--ignored-directories',
        type=click.STRING,
        multiple=True,
        default=[],
        help='List of directories to ignore'
    )(function)

    function = click.option(
        '--ignored-files',
        type=click.STRING,
        multiple=True,
        default=[],
        help='List of files to ignore'
    )(function)

    function = click.option(
        '--extension',
        type=click.STRING,
        default=DEFAULT_EXTENSION,
        help='File extension to be reviewed'
    )(function)

    function = click.option(
        '--directory',
        type=click.STRING,
        default=DEFAULT_DIRECTORY,
        help='Path to the directory where the files are located'
    )(function)

    return function


def get_version():
    try:
        version = (
            subprocess.check_output(["git", "describe", "--tags"])
            .strip()
            .decode("utf-8")
        )
        return version
    except subprocess.CalledProcessError:
        return "1.0.0"


@click.group()
@common_auth_stk_options
@common_param_options
@click.version_option(get_version(), prog_name=APPLICATION_NAME)
@pass_context
def cli(ctx,
        quick_command_id, client_id, client_secret, host_stk_ai, host_token_stk_ai, realm, retry_max_attempts,
        retry_timeout, http_proxy, https_proxy,
        directory, extension, ignored_files, ignored_directories, report_directory, report_filename, limit) -> Any:
    from src.service.reviewer_service import ReviewerService
    ctx.ensure_object(dict)

    from src.config.env_config import EnvConfig
    from src.models.definitions import Definitions

    click.echo("Initializing")

    LOG.info("Loading config...")
    ctx.obj['config'] = EnvConfig(args=ctx.params)

    LOG.info("Loading param...")
    ctx.obj['definition'] = Definitions(args=ctx.params)

    LOG.info("Loading Service...")
    ctx.obj['review_service'] = ReviewerService(env_config=ctx.obj['config'])


def run(ctx, files):
    from src.utils.report_helper import create_file_with_contents

    if len(files) > 0:
        files_reviews = FileReview.list_from_dict(files=files)

        contents_by_name = ctx.obj['review_service'].run(file_reviews=files_reviews)

        create_file_with_contents(
            file_name=ctx.obj['definition'].get_report_directory(),
            root_directory=ctx.obj['definition'].get_report_filename(),
            content_by_name=contents_by_name,
        )
    else:
        logging.info("No items to analyze")

    return EXIT_SUCCESS


@cli.command()
@click.option('--base-branch', type=str, default="main", help='The Branch that should be the base for diff')
@click.option('--compare-branch', type=str, default="develop", help='The Branch should be compared to base for diff')
@click.pass_context
def review_changes(ctx, base_branch, compare_branch):
    click.echo('Analyzing changes')
    definition = ctx.obj['definition']
    files = find_all_changed_code(
        repository_path=definition.get_directory(),
        base=base_branch,
        compare=compare_branch,
        extension=definition.get_extension(),
        ignored_directories=definition.get_ignored_directories(),
        ignored_files=definition.get_ignored_files(),
    )

    click.echo(f"Foram encontrados {len(files)} arquivos alterados.")

    return run(ctx, files)


@cli.command()
@click.pass_context
def review_dir(ctx):
    click.echo('Analyzing DIR')
    definition = ctx.obj['definition']
    files = find_all_files(
        directory=definition.get_directory(),
        extension=definition.get_extension(),
        ignored_directories=definition.get_ignored_directories(),
        ignored_files=definition.get_ignored_files(),
    )

    click.echo(f"Foram encontrados {len(files)} arquivos.")

    return run(ctx, files)
