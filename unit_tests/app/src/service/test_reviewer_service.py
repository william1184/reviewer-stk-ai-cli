import unittest
from unittest import TestCase
from unittest.mock import Mock, patch

from src.models.file_review import FileReview

FILE_NAME_1 = "dir1/file.py"
FILE_NAME_2 = "dir2/file.py"

FILE_CONTENT_1 = "HI HOW ARE YOU"
FILE_CONTENT_2 = "print('x y z')"

RESPONSE_1 = "Points found:\nI am not able to perform the code review of this file."
RESPONSE_2 = "Points found:\nfile x yz deserves to have."

EXECUTION_ID_1 = "01HYRHKFPFAZK1FFF8HVKWYEDQ"
EXECUTION_ID_2 = "02HYRHKFPFAZK1FFF8HVKWYEDQ"


def call_direct(func_var, execution_id):
    return func_var(execution_id)


class TestReviewerService(TestCase):
    _mock_sts_token_service = None
    _mock_stk_execution_service = None
    _mock_stk_callback_service = None
    _mock_pool = None
    _service = None

    @patch("multiprocessing.Pool")
    def setUp(self, mock_pool):
        self._mock_pool = mock_pool
        self._mock_sts_token_service = Mock()
        self._mock_stk_execution_service = Mock()
        self._mock_stk_callback_service = Mock()
        from src.service.reviewer_service import ReviewerService

        self._service = ReviewerService(
            stk_token_service=self._mock_sts_token_service,
            stk_execution_service=self._mock_stk_execution_service,
            stk_callback_service=self._mock_stk_callback_service,
        )

    def test__when_one_review_received__then_return_one_review(self):
        # arrange
        review = FileReview(name=FILE_NAME_1, content=FILE_CONTENT_1)

        self._mock_stk_execution_service.create.return_value = EXECUTION_ID_1
        self._mock_stk_callback_service.find.return_value = {
            "conversation_id": "01HYRHKFPF9PNNJQ91AKRX98PZ",
            "review": RESPONSE_1,
        }
        # act
        contents_by_name = self._service.run(file_reviews=[review])

        # assert
        self.assertEqual(
            {
                "dir1/file.py": "Points found:\n"
                "I am not able to perform the code review of this file."
            },
            contents_by_name,
        )

        self._mock_stk_execution_service.create.assert_called_once()
        self._mock_stk_callback_service.find.assert_called_once()

    def test__when_two_reviews_received__then_return_two_reviews(self):

        # arrange

        mock_pool_instance = self._mock_pool.return_value
        mock_pool_instance.map.return_value = [
            {
                "conversation_id": "02HYRHKFPF9PNNJQ91AKRX98PZ",
                "review": RESPONSE_2,
                "execution_id": EXECUTION_ID_2,
            }
        ]
        review_1 = FileReview(name=FILE_NAME_1, content=FILE_CONTENT_1)
        review_2 = FileReview(name=FILE_NAME_2, content=FILE_CONTENT_2)

        self._mock_stk_execution_service.create.side_effect = [
            EXECUTION_ID_1,
            EXECUTION_ID_2,
        ]

        self._mock_stk_callback_service.find.side_effect = [
            {
                "conversation_id": "01HYRHKFPF9PNNJQ91AKRX98PZ",
                "review": RESPONSE_1,
                "execution_id": EXECUTION_ID_1,
            }
        ]

        # act
        contents_by_name = self._service.run(file_reviews=[review_1, review_2])

        # assert
        self.assertEqual(
            {
                "dir1/file.py": "Points found:\n"
                "I am not able to perform the code review of this file.",
                "dir2/file.py": "Points found:\nfile x yz deserves to have.",
            },
            contents_by_name,
        )

        self.assertEqual(2, self._mock_stk_execution_service.create.call_count)
        self.assertEqual(1, self._mock_stk_callback_service.find.call_count)

    def test__when_no_file_received__then_return_empty_array(self):
        # arrange
        reviews = []

        response = self._service.run(file_reviews=reviews)

        # assert
        self.assertEqual(0, len(response))

        self._mock_stk_execution_service.create.assert_not_called()
        self._mock_stk_callback_service.find.assert_not_called()


if __name__ == "__main__":
    unittest.main()
