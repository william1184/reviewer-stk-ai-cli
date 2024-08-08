import logging
from multiprocessing import Pool, cpu_count
from typing import Dict, List

import click

from src.models.file_review import FileReview
from src.service.stk_callback_service import StkCallbackService
from src.service.stk_execution_service import StkExecutionService
from src.service.stk_token_service import StkTokenService
from src.utils.constants import APPLICATION_NAME
from src.utils.git_helper import find_all_changed_code

logger = logging.getLogger(APPLICATION_NAME)


class ReviewerService:
    _stk_execution_service: StkExecutionService
    _stk_callback_service: StkCallbackService

    def __init__(
            self,
            env_config=None,
            stk_token_service=None,
            stk_execution_service=None,
            stk_callback_service=None,
    ):
        stk_token_service = stk_token_service or StkTokenService(env_config=env_config)

        self._stk_execution_service = stk_execution_service or StkExecutionService(
            env_config=env_config, stk_token_service=stk_token_service
        )
        self._stk_callback_service = stk_callback_service or StkCallbackService(
            env_config=env_config, stk_token_service=stk_token_service
        )

    def run(self, file_reviews: List[FileReview]) -> Dict[str, str]:
        logger.info("Starting file review")

        content_by_filename = dict()

        if len(file_reviews) > 0:

            self._send_to_ai(review=file_reviews[0])
            self._find_callback_review(review=file_reviews[0])
            content_by_filename[file_reviews[0].name] = file_reviews[0].review

            with click.progressbar(file_reviews[1:]) as bar:
                for file_review in file_reviews[1:]:
                    self._send_to_ai(review=file_review)

            filename_by_execution_id = {}
            with click.progressbar(file_reviews[1:]) as bar:
                for file_review in file_reviews[1:]:
                    file_review.conversation_id = file_reviews[0].conversation_id
                    filename_by_execution_id[file_review.execution_id] = file_review.name

            content_by_filename.update(
                self._run_parallel(filename_by_execution_id=filename_by_execution_id)
            )

        logger.info("File review completed")

        return content_by_filename

    def _send_to_ai(self, review: FileReview) -> None:
        logger.info(f"Sending file: {review.name} for processing")
        execution_id = self._stk_execution_service.create(
            file_content=review.content, conversation_id=review.conversation_id
        )
        review.execution_id = execution_id
        logger.info(f"Execution created {review.execution_id}")

    def _find_callback_review(self, review: FileReview) -> None:
        logger.info(f"Fetching response for file: {review.name} completed")

        callback_response: dict = self._stk_callback_service.find(
            execution_id=review.execution_id
        )

        review.review = callback_response["review"]
        review.conversation_id = callback_response["conversation_id"]

        logger.info(f"Execution of file: {review.name} completed")

    def _run_parallel(self, filename_by_execution_id: Dict):
        pool = Pool(cpu_count())
        try:
            execution_ids = list(filename_by_execution_id.keys())

            reviews = pool.map(
                self._stk_callback_service.find, [ID for ID in execution_ids]
            )

            content_by_filename = {}
            for _review in reviews:
                execution_id = _review["execution_id"]
                file_name = filename_by_execution_id[execution_id]
                content_by_filename[file_name] = _review["review"]

            return content_by_filename

        except Exception:
            logger.exception("Multiprocessing error")
            raise
        finally:
            logger.info("Review execution ended!")
            pool.close()


__all__ = ["ReviewerService"]
