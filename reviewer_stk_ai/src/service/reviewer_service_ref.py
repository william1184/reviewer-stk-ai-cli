import logging
from multiprocessing import Pool, cpu_count
from typing import List, Dict

from reviewer_stk_ai.src.service.stk_callback_service import StkCallbackService
from reviewer_stk_ai.src.service.stk_execution_service import StkExecutionService
from reviewer_stk_ai.src.utils.constants import APPLICATION_NAME, TEMP_PATH
from src.utils.file_helper import create_file_and_directory

logger = logging.getLogger(APPLICATION_NAME)


class ReviewerService:
    _stk_execution_service: StkExecutionService
    _stk_callback_service: StkCallbackService

    _conversation_id: str

    def __init__(
        self,
        stk_execution_service=None,
        stk_callback_service=None,
    ):
        self._stk_execution_service = stk_execution_service
        self._stk_callback_service = stk_callback_service

    def run(self, files: Dict) -> List[Dict]:
        logger.info("Starting file review")
        results = []

        if len(files) <= 0:
            logger.info("No files to review")
            return results

        results.append(self.process_review(file=files[0]))
        if len(files) > 1:
            results.extend(
                self._run_parallel(
                    files=files[1:],
                )
            )

        logger.info("File review completed")

        return results

    def process_review(self, file: Dict) -> Dict:
        execution_id = self._send_to_ai(file=file)

        llm_review = self._find_callback_review(execution_id=execution_id)

        response_tmp_file_path = self._store_temp_review(
            execution_id=execution_id, file_name=file["name"], llm_review=llm_review
        )

        return {
            "file_name": file["name"],
            "execution_id": execution_id,
            "conversation_id": self._conversation_id,
            "response_tmp_file_path": response_tmp_file_path,
        }

    def _send_to_ai(self, file: Dict) -> str:
        logger.info(
            f"Sending file: {file['name']} for processing. Conversation_id: {self._conversation_id}"
        )

        execution_id = self._stk_execution_service.create(
            file_content=file["content"], conversation_id=self._conversation_id
        )

        logger.info(f"Execution created {execution_id}")

        return execution_id

    def _find_callback_review(self, execution_id: str) -> str:
        logger.info(f"Fetching response for execution_id: {execution_id}")

        callback_response: dict = self._stk_callback_service.find(
            execution_id=execution_id
        )

        if self._conversation_id is None:
            self._conversation_id = callback_response["conversation_id"]

        logger.info(f"Execution of execution_id: {execution_id} completed")

        return callback_response["review"]

    def _run_parallel(self, files: List[Dict]) -> List[Dict]:
        pool = Pool(cpu_count())
        try:
            results = pool.map(self.process_review, [file for file in files])

            return results
        except Exception:
            logger.exception("Multiprocessing error")
            raise
        finally:
            logger.info("Review execution ended!")
            pool.close()

    @staticmethod
    def _store_temp_review(execution_id: str, file_name: str, llm_review: str):
        tmp_file_name = f"{execution_id}"
        llm_review_final = "".join((f"File name: {file_name} \n\n", llm_review))
        path = create_file_and_directory(TEMP_PATH, tmp_file_name, llm_review_final)
        return path


__all__ = ["ReviewerService"]
