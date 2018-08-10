# Copyright 2018 BLEMUNDSBURY AI LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
