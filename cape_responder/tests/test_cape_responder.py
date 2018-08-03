from cape_responder.responder_core import Responder
from cape_document_manager.document_store import DocumentStore
from pprint import pprint


def test_inline_text():
    response = Responder.get_answers_from_documents('fake-user', 'what day is today ?', text='Today is Tuesday.',
                                                    document_ids=None)
    pprint(response)
    assert response[0]['answerText'] == 'Tuesday'


def test_documents():
    DocumentStore.create_document('fake-user', 'doc1', 'Test document', 'This is a test', replace=True, document_id='doc1')
    DocumentStore.get_documents('fake-user')
    response = Responder.get_answers_from_documents('fake-user', 'What is this?', document_ids=['doc1'])
    pprint(response)
    assert response[0]['sourceId'] == 'doc1'
    DocumentStore.delete_document('fake-user', 'doc1')


def test_document_embeddings():
    DocumentStore.create_document('fake-user', 'doc1', 'Test document', 'This is a test', replace=True, document_id='doc1', get_embedding=Responder.get_document_embeddings)
    response = Responder.get_answers_from_documents('fake-user', 'What is this?', document_ids=['doc1'])
    pprint(response)
    assert response[0]['sourceId'] == 'doc1'
    DocumentStore.delete_document('fake-user', 'doc1')
