from cape_document_manager.document_store import DocumentStore
from cape_document_manager.annotation_store import AnnotationStore
import pytest

@pytest.fixture(scope="session")
def cleanup():
    for annotation in AnnotationStore.get_annotations('fake-user'):
        AnnotationStore.delete_annotation('fake-user', annotation['id'])
    for document in DocumentStore.get_documents('fake-user'):
        DocumentStore.delete_document('fake-user', document['id'])
