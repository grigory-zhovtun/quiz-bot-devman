from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def read_quiz_file_content(filepath: str) -> str:
    with open(filepath, 'r', encoding='KOI8-R') as quiz_file:
        return quiz_file.read()


def parse_questions_and_answers_from_file(filepath: str) -> dict[str, str]:
    file_content = read_quiz_file_content(filepath)
    content_blocks = file_content.split('\n\n')

    questions_and_answers = {}
    current_question_text = None

    for block in content_blocks:
        if block.startswith('Вопрос'):
            question_without_number = block.split(':\n', maxsplit=1)[1]
            current_question_text = question_without_number

        elif block.startswith('Ответ') and current_question_text:
            answer_text = block.split(':\n', maxsplit=1)[1]
            questions_and_answers[current_question_text] = answer_text

    return questions_and_answers


def load_all_questions_from_directory(directory_path: str) -> dict[str, str]:
    all_questions_and_answers = {}
    for quiz_filename in os.listdir(directory_path):
        if not quiz_filename.endswith('.txt'):
            continue
        filepath = os.path.join(directory_path, quiz_filename)
        file_questions = parse_questions_and_answers_from_file(filepath)
        all_questions_and_answers.update(file_questions)
    return all_questions_and_answers


def clean_quiz_answer(raw_answer: str) -> str:
    cleaned = raw_answer.split('.')[0]
    cleaned = cleaned.split('(')[0]
    return cleaned.strip()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    quiz_files_directory = 'quiz-questions'
    all_quiz_files = os.listdir(quiz_files_directory)
    first_quiz_file = all_quiz_files[0]
    full_path_to_quiz_file = os.path.join(quiz_files_directory, first_quiz_file)

    logger.info('Читаю файл: %s', first_quiz_file)

    questions_with_answers = parse_questions_and_answers_from_file(full_path_to_quiz_file)

    for question, answer in list(questions_with_answers.items())[:3]:
        logger.info('Вопрос: %s...', question[:80])
        logger.info('Ответ: %s', answer)
