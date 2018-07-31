from cape_responder.responder_core import Responder
from pprint import pprint


def test_cape_responder():
    response = Responder.get_answers_from_documents('fake-user', 'what day is today ?', text='Today is Tuesday.',
                                                    document_ids=None)

    pprint(response)
    pprint(list(response))
