import logging
from multiprocessing import Pool, cpu_count
from typing import List

from reviewer_stk_ai.src.models.file_review import FileReview
from reviewer_stk_ai.src.service.stk_callback_service import StkCallbackService
from reviewer_stk_ai.src.service.stk_execution_service import StkExecutionService
from reviewer_stk_ai.src.utils.constants import APPLICATION_NAME, TEMP_PATH
from src.utils.file_helper import create_file_and_directory

logger = logging.getLogger(APPLICATION_NAME)


class ReviewerService:
    _stk_execution_service: StkExecutionService
    _stk_callback_service: StkCallbackService

    def __init__(
        self,
        stk_execution_service=None,
        stk_callback_service=None,
    ):
        self._stk_execution_service = stk_execution_service
        self._stk_callback_service = stk_callback_service

    def run(self, file_reviews: List[FileReview]) -> None:
        logger.info("Starting file review")

        if len(file_reviews) > 0:

            self.process_review(review=file_reviews[0])

            for file_review in file_reviews[1:]:
                file_review.conversation_id = file_reviews[0].conversation_id

            self._run_parallel(
                file_reviews=file_reviews[1:],
            )

        logger.info("File review completed")

    def process_review(self, review):
        self._send_to_ai(review=review)
        self._find_callback_review(review=review)
        self._store_temp_review(review=review)

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

        review.llm_review = callback_response["review"]
        review.conversation_id = callback_response["conversation_id"]

        logger.info(f"Execution of file: {review.name} completed")

    def _run_parallel(self, file_reviews: List[FileReview]):
        pool = Pool(cpu_count())
        try:
            pool.map(self.process_review, [review for review in file_reviews])

        except Exception:
            logger.exception("Multiprocessing error")
            raise
        finally:
            logger.info("Review execution ended!")
            pool.close()

    @staticmethod
    def _store_temp_review(review: FileReview):
        file_name = f"{review.execution_id}"
        llm_review = "".join((f"File name: {review.name} \n\n", review.llm_review))
        create_file_and_directory(TEMP_PATH, file_name, llm_review)


__all__ = ["ReviewerService"]
