from typing import List


class Response:
    answer_text: str
    answer_context: str
    confidence: float
    source_id: str
    source_type: str
    answer_text_start_offset: int
    answer_text_end_offset: int
    answer_context_start_offset: int
    answer_context_end_offset: int

    def __init__(self, answer_text: str, answer_context: str, confidence: float, source_id: str, source_type: str,
                 answer_text_start_offset: int, answer_text_end_offset: int,
                 answer_context_start_offset: int, answer_context_end_offset: int):
        self.answer_text = answer_text
        self.answer_context = answer_context
        self.confidence = confidence
        self.source_id = source_id
        self.source_type = source_type
        self.answer_text_start_offset = answer_text_start_offset
        self.answer_text_end_offset = answer_text_end_offset
        self.answer_context_start_offset = answer_context_start_offset
        self.answer_context_end_offset = answer_context_end_offset


class ResponderAnswer:
    responses: List[Response]

    def __init__(self, responses: List[Response]):
        assert responses, "Responses can not be empty"
        self.responses = responses
