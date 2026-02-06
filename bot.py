import logging

from dotenv import load_dotenv
from os import getenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def handle_start_command(update: Update, context: CallbackContext):
    update.message.reply_text('Здравствуйте')


def echo_user_message(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


if __name__ == '__main__':
    load_dotenv()
    telegram_bot_token = getenv('TELEGRAM_BOT_TOKEN')

    updater = Updater(telegram_bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', handle_start_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_user_message))

    updater.start_polling()
    updater.idle()
