#  -*- encoding: utf-8 -*-


from app.common.constants_and_variables import AppConstants, AppVariables


class TelegramClient:

    def __init__(self):
        self.bot_constants = AppConstants()
        self.bot_variables = AppVariables()

    def api_send_message(self):
        return self.bot_constants.API_TELEGRAM_SEND_MESSAGE.format(bot_token=self.bot_variables.telegram_bot_token)
