# -*- coding: utf-8 -*-

import logging
import io

from base_faq_storage import BaseFaqStorage


class PlainFileFaqStorage(BaseFaqStorage):
    """Реализация хранилища FAQ на базе простого текстового файла без разметки"""
    def __init__(self, path):
        self.path = path
        self.loaded = False
        self.questions = []
        self.answers = []
        self.logger = logging.getLogger('PlainFileFaqStorage')

    def __load_entries(self):
        if not self.loaded:
            self.loaded = True

            logging.info(u'Start loading QA entries from {}'.format(self.path))
            with io.open(self.path, 'r', encoding='utf-8') as rdr:
                for line in rdr:
                    line = line.strip()
                    if len(line) > 0:
                        if line[0] == u'#':
                            # строки с комментариями начинаются с #
                            continue
                        elif line.startswith(u'Q:'):
                            # Может быть один или несколько вариантов вопросов для одного ответа.
                            # Строки вопросов начинаются с паттерна "Q:"

                            alt_questions = []
                            question = line.replace(u'Q:', u'').strip()
                            assert(len(question) > 0)
                            alt_questions.append(question)

                            answer_lines = []

                            for line in rdr:
                                if line.startswith(u'Q:'):
                                    question = line.replace(u'Q:', u'').strip()
                                    assert (len(question) > 0)
                                    alt_questions.append(question)
                                else:
                                    answer_lines.append(line.replace(u'A:', u'').strip())
                                    break

                            # Теперь считываем все строки до первой пустой, считая
                            # их строками ответа
                            for line2 in rdr:
                                line2 = line2.strip()
                                if len(line2) == 0:
                                    break
                                else:
                                    answer_lines.append(line2.replace(u'A:', u'').strip())

                            answer = u' '.join(answer_lines)
                            assert(len(answer) > 0)

                            if answer.startswith('---'):
                                # для удобства отладки демо-faq'ов, где ответы прописаны как --------
                                answer = u'<<<<dummy answer for>>> ' + question

                            for question in alt_questions:
                                self.questions.append(question)
                                self.answers.append(answer)

            self.logger.info(u'{} QA entries loaded from {}'.format(len(self.questions), self.path))

    def get_most_similar(self, question_str, similarity_detector, word_embeddings, text_utils):
        assert question_str
        self.__load_entries()

        question2 = u' '.join(text_utils.tokenize(question_str))
        best_question, best_rel = similarity_detector.get_most_similar(question2,
                                                                       [(s, None, None) for s in self.questions],
                                                                       text_utils,
                                                                       word_embeddings,
                                                                       nb_results=1)
        question_index = self.questions.index(best_question)
        best_answer = self.answers[question_index]
        return best_answer, best_rel, best_question

