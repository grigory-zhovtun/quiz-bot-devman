import logging
import os
import random

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from read_quiz_files import parse_questions_and_answers_from_file

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def load_all_questions_from_directory(directory_path):
    all_questions_and_answers = {}
    for quiz_filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, quiz_filename)
        file_questions = parse_questions_and_answers_from_file(filepath)
        all_questions_and_answers.update(file_questions)
    return all_questions_and_answers


def handle_start_command(update: Update, context: CallbackContext):
    quiz_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(quiz_keyboard)
    update.message.reply_text('Привет! Я бот для викторины!', reply_markup=reply_markup)


def handle_new_question_request(update: Update, context: CallbackContext):
    random_question = random.choice(list(context.bot_data['questions_and_answers']))
    update.message.reply_text(random_question)


def handle_user_message(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


if __name__ == '__main__':
    load_dotenv()
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    updater = Updater(telegram_bot_token)
    dispatcher = updater.dispatcher

    dispatcher.bot_data['questions_and_answers'] = load_all_questions_from_directory('quiz-questions')

    dispatcher.add_handler(CommandHandler('start', handle_start_command))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_message))

    updater.start_polling()
    updater.idle()
