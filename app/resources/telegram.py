#  -*- encoding: utf-8 -*-

import logging
import traceback

import requests

from app.clients.telegram import TelegramClient
from app.common.constants_and_variables import AppVariables


class TelegramResource:

    def __init__(self):
        self.telegram_client = TelegramClient()
        self.api_send_message = self.telegram_client.api_send_message()
        self.app_variables = AppVariables()

    def send(self, data):
        try:
            logging.info("Sending message: %s", data)
            response = requests.post(self.api_send_message, data=data)
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error("Something went wrong. Exception: %s", traceback.format_exc())

    def send_message(self, message, chat_id=None, shadow=True, parse_mode='Markdown', disable_web_page_preview=True,
                     disable_notification=False, reply_markup=None):
        data = {
            'chat_id': chat_id if chat_id is not None else self.app_variables.shadow_mode_chat_id,
            'text': '{message}'.format(message=message),
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
            'disable_notification': disable_notification,
            'reply_markup': reply_markup
        }

        self.send(data)

        if chat_id is not None and shadow and self.app_variables.shadow_mode:
            data['chat_id'] = self.app_variables.shadow_mode_chat_id
            self.send(data)
