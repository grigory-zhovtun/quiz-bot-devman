import logging

import telegram


class TelegramLogsHandler(logging.Handler):

    def __init__(self, telegram_token: str, chat_id: str):
        super().__init__()
        self.bot = telegram.Bot(token=telegram_token)
        self.chat_id = chat_id

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)
