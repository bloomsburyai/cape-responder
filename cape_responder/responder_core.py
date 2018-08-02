from math import ceil
from typing import List, Tuple, Dict, Optional
import json
import numpy as np
from hashlib import sha256
from functools import partial
from bisect import bisect_right
from cape_responder.responder_settings import NUM_WORKERS_PER_REQUEST
from cape_document_manager.document_store import SearchResult, DocumentStore
from cape_document_manager.annotation_store import AnnotationStore
from cape_machine_reader.cape_machine_reader_core import MachineReader, MachineReaderConfiguration
from cape_document_qa import cape_docqa_machine_reader
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.text_responses import ERROR_INVALID_THRESHOLD
from cape_responder.task_manager import connect

THRESHOLD_MAP = {
    'savedreply': {
        'VERYHIGH': 0.7,
        'HIGH': 0.5,
        'MEDIUM': 0.25,
        'LOW': 0.15,
        'VERYLOW': 0.0
    },
    'document': {
        'VERYHIGH': 0.0,
        'HIGH': 0.,
        'MEDIUM': 0.0,
        'LOW': 0.0,
        'VERYLOW': 0.0
    }
}

SPEED_OR_ACCURACY_CHUNKS_MAP = {'speed': 0.25, 'balanced': 1, 'accuracy': 4, 'total': -1}


class Responder:
    _MACHINE_READER = None  # MachineReader()

    @staticmethod
    def get_machine_reader():
        if Responder._MACHINE_READER is None:
            machine_reader_conf = cape_docqa_machine_reader.get_production_model_config()
            machine_reader_model = cape_docqa_machine_reader.CapeDocQAMachineReaderModel(machine_reader_conf)
            Responder._MACHINE_READER = MachineReader(machine_reader_model)
        return Responder._MACHINE_READER

    @staticmethod
    def split_chunks(l, number_of_workers):
        divided_chunks = []
        for i in range(0, len(l), number_of_workers):
            divided_chunks.append(l[i:i + number_of_workers])
        return divided_chunks

    @staticmethod
    def get_machine_reader_configuration(offset=0, number_of_items=1, threshold='MEDIUM'):
        top_k = number_of_items + offset
        try:
            threshold_value = THRESHOLD_MAP['document'][threshold]
        except KeyError:
            raise UserException(ERROR_INVALID_THRESHOLD)
        return MachineReaderConfiguration(threshold_reader=threshold_value, top_k=top_k)

    @staticmethod
    def get_answers_from_similar_questions(
            user_token: str,
            question: str,
            type: str = 'all',
            document_ids: List[str] = None,
            threshold: str = 'MEDIUM'
    ) -> List[dict]:
        """
        Returns answers from the most similar saved replies and annotations.
        :param user_token:                          User's ID token
        :param question:                            question in string format
        :param type:                                'saved_reply', 'annotation' or 'all'
        :param document_ids:                        Limit annotation search to specified document IDs
        :param threshold:                           Only return results with the given confidence
        """
        type_to_param = {'all': None, 'saved_reply': True, 'annotation': False}
        results = AnnotationStore.similar_annotations(user_token, question, document_ids,
                                                      saved_replies=type_to_param[type])
        threshold_value = THRESHOLD_MAP['savedreply'][threshold]
        results = list(filter(lambda reply: reply['confidence'] >= threshold_value, results))
        return results

    @staticmethod
    def get_answers_from_documents(
            user_token: str,
            question: str,
            document_ids: Optional[List[str]] = None,
            offset: int = 0,
            number_of_items: int = 1,
            text: str = None,
            threshold: str = 'MEDIUM',
            speed_or_accuracy: str = 'balanced',
    ) -> List[dict]:
        """
        Returns answers from a user's documents

        :param user_token:      User's ID token
        :param question:        Question in string format
        :param document_ids:    Limit search to specified document IDs
        :param text:            Search for an answer in the given text
        """
        results = []
        if text is not None:
            temp_id = 'Inline text-' + sha256(text.encode('utf-8')).hexdigest()
            DocumentStore.create_document(user_token, "Inline text", "Inline text", text,
                                          document_id=temp_id, replace=True,
                                          get_embedding=Responder.get_empty_embeddings)  # Don't generate embeddings for
            # inline documents
            if document_ids is not None:
                document_ids.append(temp_id)
            else:
                document_ids = [temp_id]
        speed_or_accuracy_coef = SPEED_OR_ACCURACY_CHUNKS_MAP[speed_or_accuracy]
        if speed_or_accuracy_coef > 0:
            limit_per_doc = int(ceil(number_of_items * NUM_WORKERS_PER_REQUEST * speed_or_accuracy_coef))
        else:
            limit_per_doc = None
        chunk_results = list(DocumentStore.search_chunks(user_token, question, document_ids=document_ids,
                                                         limit_per_doc=limit_per_doc))
        if len(chunk_results) == 0:
            # We don't have any matching documents
            return []
        worker_chunks = Responder.split_chunks(chunk_results, NUM_WORKERS_PER_REQUEST)
        respond = partial(Responder.machine_reader_logits, question)
        future_answers: List = connect().map(respond, worker_chunks)
        machine_reader_configuration = Responder.get_machine_reader_configuration(offset, number_of_items)
        reduced_answers = connect().submit(Responder.reduce_results, future_answers,
                                           machine_reader_configuration,
                                           worker_chunks)
        results.extend(reduced_answers.result())
        if text is not None:
            DocumentStore.delete_document(user_token, temp_id)

        threshold_value = THRESHOLD_MAP['document'].get(threshold, THRESHOLD_MAP['document']['MEDIUM'])

        results = list(filter(lambda reply: reply['confidence'] >= threshold_value, results))

        return results

    @staticmethod
    def machine_reader_logits(
            question: str,
            results: List[SearchResult]
    ) -> List[Tuple[Tuple[np.array, np.array], Tuple[int, int]]]:
        """
        Returns answers for the question sourced from the given range.
        :param user_token: User's token to identify document embedding cache to use
        :param question: question in string format
        :param results: List of SearchResults to process by this worker
        """
        logits = []
        for result in results:
            fields = result.get_indexable_string_fields()
            embedding = None
            if len(fields['embedding']) > 0:
                embedding = np.asarray(json.loads(fields['embedding']))
            logits.append(
                Responder.get_machine_reader().get_logits(
                    result.matched_content, question, fields['overlap_before'],
                    fields['overlap_after'], document_embedding=embedding)
            )
        return logits

    @staticmethod
    def combine_chunks(future_answers, chunks: List[SearchResult]):
        flat_logits = []
        flat_overlaps = []
        flat_text = ""
        positions = {}
        for chunk_idx, answers in enumerate(future_answers):
            for group_idx, answer in enumerate(answers):
                search_result = chunks[chunk_idx][group_idx]
                flat_logits.append(answer[0])
                flat_overlaps.append(answer[1])
                fields = search_result.get_indexable_string_fields()
                # position in flat_text corresponds to position in doc_id starting at text_span[0]
                positions[len(flat_text)] = (fields['document_id'],) + tuple(json.loads(fields['text_span']))
                flat_text += " " + search_result.matched_content
        return flat_logits, flat_overlaps, flat_text, positions

    @staticmethod
    def translate_spans(answer_spans: List[Tuple[int, int]], context_spans: List[Tuple[int, int]],
                        positions: Dict[int, Tuple[str, int, int]]) -> List[
        Tuple[str, int, int]]:
        """Take spans from combined chunks and return the original document id and span"""
        offsets, references = list(zip(*sorted(positions.items())))
        results = []
        for answer_idx, span in enumerate(answer_spans):
            context_span = context_spans[answer_idx]
            idx = bisect_right(offsets, span[0]) - 1
            doc_id, doc_beg, doc_end = references[idx]
            # We do -1 because we add a space when combining
            new_span_beg = doc_beg + (span[0] - offsets[idx] - 1)
            full_context_span_beg = doc_beg + (context_span[0] - offsets[idx] - 1)
            new_context_span_beg = max(full_context_span_beg, doc_beg)
            new_span_end = min(doc_beg + (span[1] - offsets[idx] - 1), doc_end)
            full_context_span_end = doc_beg + (context_span[1] - offsets[idx] - 1)
            new_context_span_end = min(full_context_span_end, doc_end)
            results.append((doc_id, new_span_beg, new_span_end,
                            new_context_span_beg, new_context_span_end,
                            new_context_span_beg - full_context_span_beg,
                            full_context_span_end - new_context_span_end
                            ))
        return results

    @staticmethod
    def reduce_results(future_answers, machine_reader_configuration: MachineReaderConfiguration,
                       chunks: List[SearchResult]) -> List[dict]:
        flat_logits, flat_overlaps, flat_text, positions = Responder.combine_chunks(future_answers, chunks)
        results = []
        answer_spans = []
        answer_context_spans = []
        for answer in Responder.get_machine_reader().get_answers_from_logits(machine_reader_configuration, flat_logits,
                                                                             flat_overlaps, flat_text):
            results.append({
                "answerText": answer.text,
                "answerContext": answer.long_text,
                "confidence": float(answer.score_reader),
                "sourceType": 'document',
                "sourceId": None,
                "answerTextStartOffset": None,
                "answerTextEndOffset": None,
                "answerContextStartOffset": None,
                "answerContextEndOffset": None
            })
            # TODO long text spans
            answer_spans.append(answer.span)
            answer_context_spans.append(answer.long_text_span)
        for (idx, (doc_id, answer_beg_span, answer_end_span,
                   context_beg_span, context_end_span,
                   context_diff_beg, context_diff_end)) in enumerate(
            Responder.translate_spans(answer_spans, answer_context_spans, positions)):
            results[idx]["sourceId"] = doc_id
            results[idx]["answerTextStartOffset"] = answer_beg_span
            results[idx]["answerTextEndOffset"] = answer_end_span
            results[idx]["answerContextStartOffset"] = context_beg_span
            results[idx]["answerContextEndOffset"] = context_end_span
            answer_range = answer_end_span - answer_beg_span
            results[idx]["answerText"] = results[idx]["answerText"][:answer_range]
            results[idx]["answerContext"] = results[idx]["answerContext"][
                                            context_diff_beg:(-context_diff_end) if context_diff_end else None]
            # debug("----Translating answer text spans took", time.time() - tic)
        return results

    @staticmethod
    def get_document_embeddings(text):
        return json.dumps(Responder.get_machine_reader().get_document_embedding(text).tolist())

    @staticmethod
    def get_empty_embeddings(text):
        return ''
