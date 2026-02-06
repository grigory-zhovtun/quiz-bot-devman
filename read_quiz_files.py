import os


def read_quiz_file_content(filepath):
    with open(filepath, 'r', encoding='KOI8-R') as quiz_file:
        return quiz_file.read()


def parse_questions_and_answers_from_file(filepath):
    file_content = read_quiz_file_content(filepath)
    content_blocks = file_content.split('\n\n')

    questions_and_answers = {}

    current_question_text = None

    for block in content_blocks:
        if block.startswith('Вопрос'):
            question_without_number = block.split(':\n', maxsplit=1)[1]
            current_question_text = question_without_number

        elif block.startswith('Ответ'):
            answer_text = block.split(':\n', maxsplit=1)[1]
            questions_and_answers[current_question_text] = answer_text

    return questions_and_answers


if __name__ == '__main__':
    quiz_files_directory = 'quiz-questions'

    all_quiz_files = os.listdir(quiz_files_directory)
    first_quiz_file = all_quiz_files[0]

    full_path_to_quiz_file = os.path.join(quiz_files_directory, first_quiz_file)

    print(f'Читаю файл: {first_quiz_file}')
    print('=' * 50)

    questions_with_answers = parse_questions_and_answers_from_file(full_path_to_quiz_file)

    for question, answer in list(questions_with_answers.items())[:3]:
        print(f'Вопрос: {question[:80]}...')
        print(f'Ответ: {answer}')
        print('-' * 50)
