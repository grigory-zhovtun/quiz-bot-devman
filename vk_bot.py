from __future__ import annotations

import logging
import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from read_quiz_files import load_all_questions_from_directory, clean_quiz_answer
from telegram_log_handler import TelegramLogsHandler

logger = logging.getLogger(__name__)


def build_quiz_keyboard() -> VkKeyboard:
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)
    return keyboard


def send_message(event, vk_api, keyboard: VkKeyboard, message: str) -> None:
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 2**31),
    )


def handle_new_question_request(
    event, vk_api, keyboard: VkKeyboard,
    redis_connection: redis.Redis, questions_and_answers: dict[str, str],
) -> None:
    random_question = random.choice(list(questions_and_answers))
    redis_connection.set(f'vk-{event.user_id}', random_question)
    send_message(event, vk_api, keyboard, random_question)


def handle_solution_attempt(
    event, vk_api, keyboard: VkKeyboard,
    redis_connection: redis.Redis, questions_and_answers: dict[str, str],
) -> None:
    current_question = redis_connection.get(f'vk-{event.user_id}')

    if not current_question:
        send_message(event, vk_api, keyboard, 'Напиши «Новый вопрос», чтобы начать!')
        return

    correct_answer = questions_and_answers[current_question]
    cleaned_correct_answer = clean_quiz_answer(correct_answer)

    if event.text.lower() == cleaned_correct_answer.lower():
        send_message(event, vk_api, keyboard, 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос».')
    else:
        send_message(event, vk_api, keyboard, 'Неправильно... Попробуешь ещё раз?')


def handle_give_up(
    event, vk_api, keyboard: VkKeyboard,
    redis_connection: redis.Redis, questions_and_answers: dict[str, str],
) -> None:
    current_question = redis_connection.get(f'vk-{event.user_id}')

    if not current_question:
        send_message(event, vk_api, keyboard, 'Напиши «Новый вопрос», чтобы начать!')
        return

    correct_answer = questions_and_answers[current_question]
    send_message(event, vk_api, keyboard, f'Правильный ответ: {correct_answer}')
    handle_new_question_request(event, vk_api, keyboard, redis_connection, questions_and_answers)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    load_dotenv()

    telegram_logs_handler = TelegramLogsHandler(
        os.environ['TELEGRAM_BOT_TOKEN'], os.environ['TELEGRAM_CHAT_ID'],
    )
    logger.addHandler(telegram_logs_handler)

    vk_session = vk.VkApi(token=os.environ['VK_GROUP_TOKEN'])
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    redis_connection = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True,
    )

    questions_and_answers = load_all_questions_from_directory('quiz-questions')
    quiz_keyboard = build_quiz_keyboard()

    for event in longpoll.listen():
        try:
            if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
                continue
            if event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api, quiz_keyboard, redis_connection, questions_and_answers)
            elif event.text == 'Сдаться':
                handle_give_up(event, vk_api, quiz_keyboard, redis_connection, questions_and_answers)
            else:
                handle_solution_attempt(event, vk_api, quiz_keyboard, redis_connection, questions_and_answers)
        except Exception:
            logger.exception('Ошибка при обработке сообщения ВКонтакте')
