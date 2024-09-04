from typing import List, Dict

from src.utils.hash_helper import generate_file_hash


class FileReview:
    """
    Class to analyze a file

    Attributes:
        name (str): File name.
        content (str): File content.
        execution_id (str): ID analyze execution.
        conversation_id (str): ID of llm conversation.
        llm_review (str): File analyze response.
    """

    name: str
    content: str
    execution_id: str
    conversation_id: str
    llm_review: str

    def __init__(
        self,
        execution_id: str = "",
        conversation_id: str = "",
        name: str = "",
        content: str = "",
        llm_review: str = "",
    ):
        self.name = name
        self.content = content
        self.execution_id = execution_id
        self.conversation_id = conversation_id
        self.llm_review = llm_review
        self.file_content_hash = generate_file_hash(self.content)

    def __str__(self):
        return (
            f"FileReview(\n"
            f"  Name: {self.name}\n"
            f"  Content: {self.content[:10]}{'...' if len(self.content) > 10 else ''}\n"
            f"  Execution ID: {self.execution_id}\n"
            f"  Conversation ID: {self.conversation_id}\n"
            f"  Review: {self.llm_review[:10]}{'...' if len(self.llm_review) > 10 else ''}\n"
            f")"
        )

    @staticmethod
    def list_from_dict(files: Dict[str, str]) -> List:
        files_reviews = []
        if len(files) > 0:
            for _file_path in files:
                review = FileReview(name=_file_path, content=files[_file_path])
                files_reviews.append(review)

        return files_reviews
