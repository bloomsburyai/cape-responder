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

from cape_responder.responder_core import Responder
from cape_document_manager.document_store import DocumentStore
from cape_document_manager.annotation_store import AnnotationStore
from pprint import pprint
import pytest


def test_inline_text():
    response = Responder.get_answers_from_documents('fake-user', 'what day is today ?', text='Today is Tuesday.',
                                                    document_ids=None)
    pprint(response)
    assert 'Tuesday' in response[0]['answerText']


@pytest.mark.usefixtures('cleanup')
def test_documents():
    DocumentStore.create_document('fake-user', 'doc1', 'Test document', 'This is a test', replace=True, document_id='doc1')
    DocumentStore.get_documents('fake-user')
    response = Responder.get_answers_from_documents('fake-user', 'What is this?', document_ids=['doc1'])
    pprint(response)
    assert response[0]['sourceId'] == 'doc1'


@pytest.mark.usefixtures('cleanup')
def test_document_embeddings():
    DocumentStore.create_document('fake-user', 'doc1', 'Test document', 'This is a test', replace=True, document_id='doc1', get_embedding=Responder.get_document_embeddings)
    response = Responder.get_answers_from_documents('fake-user', 'What is this?', document_ids=['doc1'])
    pprint(response)
    assert response[0]['sourceId'] == 'doc1'


@pytest.mark.usefixtures('cleanup')
def test_saved_reply():
    saved_reply_id = AnnotationStore.create_annotation('fake-user', 'What is the time?', 'Lunch time!')
    response = Responder.get_answers_from_similar_questions('fake-user', 'What time is it?')
    pprint(response)
    assert response[0]['answerText'] == 'Lunch time!'


@pytest.mark.usefixtures('cleanup')
def test_annotation():
    annotation_id = AnnotationStore.create_annotation('fake-user', 'What is this?', 'This is an annotation', document_id='doc1', page=3, metadata = {'test': True})
    response = Responder.get_answers_from_similar_questions('fake-user', 'What is this?')
    pprint(response)
    assert response[0]['answerText'] == 'This is an annotation'
    assert response[0]['page'] == 3
    assert response[0]['metadata']['test'] == True

