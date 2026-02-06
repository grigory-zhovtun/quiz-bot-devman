import logging
import os
import random
from enum import Enum

import redis
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)

from read_quiz_files import parse_questions_and_answers_from_file

logger = logging.getLogger(__name__)


class QuizState(Enum):
    CHOOSING = 1
    ANSWERING = 2


def load_all_questions_from_directory(directory_path):
    all_questions_and_answers = {}
    for quiz_filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, quiz_filename)
        file_questions = parse_questions_and_answers_from_file(filepath)
        all_questions_and_answers.update(file_questions)
    return all_questions_and_answers


def clean_quiz_answer(raw_answer):
    cleaned = raw_answer.split('.')[0]
    cleaned = cleaned.split('(')[0]
    return cleaned.strip()


def handle_start_command(update: Update, context: CallbackContext):
    quiz_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(quiz_keyboard)
    update.message.reply_text('Привет! Я бот для викторины!', reply_markup=reply_markup)
    return QuizState.CHOOSING


def handle_new_question_request(update: Update, context: CallbackContext):
    random_question = random.choice(list(context.bot_data['questions_and_answers']))
    redis_connection = context.bot_data['redis_connection']
    redis_connection.set(update.effective_user.id, random_question)
    update.message.reply_text(random_question)
    return QuizState.ANSWERING


def handle_solution_attempt(update: Update, context: CallbackContext):
    redis_connection = context.bot_data['redis_connection']
    current_question = redis_connection.get(update.effective_user.id)

    correct_answer = context.bot_data['questions_and_answers'][current_question]
    cleaned_correct_answer = clean_quiz_answer(correct_answer)

    if update.message.text.lower() == cleaned_correct_answer.lower():
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос».')
        return QuizState.CHOOSING
    else:
        update.message.reply_text('Неправильно... Попробуешь ещё раз?')
        return QuizState.ANSWERING


def handle_give_up(update: Update, context: CallbackContext):
    redis_connection = context.bot_data['redis_connection']
    current_question = redis_connection.get(update.effective_user.id)

    correct_answer = context.bot_data['questions_and_answers'][current_question]
    update.message.reply_text(f'Правильный ответ: {correct_answer}')

    return handle_new_question_request(update, context)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    load_dotenv()
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    updater = Updater(telegram_bot_token)
    dispatcher = updater.dispatcher

    redis_connection = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True,
    )
    dispatcher.bot_data['redis_connection'] = redis_connection
    dispatcher.bot_data['questions_and_answers'] = load_all_questions_from_directory('quiz-questions')

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handle_start_command)],
        states={
            QuizState.CHOOSING: [
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
            ],
            QuizState.ANSWERING: [
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                MessageHandler(Filters.regex('^Сдаться$'), handle_give_up),
                MessageHandler(Filters.text & ~Filters.command, handle_solution_attempt),
            ],
        },
        fallbacks=[CommandHandler('start', handle_start_command)],
    )

    dispatcher.add_handler(conversation_handler)

    updater.start_polling()
    updater.idle()
