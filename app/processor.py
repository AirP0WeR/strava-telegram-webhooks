#  -*- encoding: utf-8 -*-

import logging

import scout_apm.celery
from celery import Celery

from app.commands.challenges import Challenges
from app.commands.process import Process
from app.common.constants_and_variables import AppVariables
from app.common.execution_time import execution_time
from app.resources.telegram import TelegramResource

app_variables = AppVariables()
process = Process()
telegram_resource = TelegramResource()
challenges = Challenges()

app = Celery()
app.conf.BROKER_URL = app_variables.redis_url
app.conf.BROKER_POOL_LIMIT = 0
app.conf.SCOUT_MONITOR = app_variables.scout_monitor
app.conf.SCOUT_NAME = app_variables.scout_name
app.conf.SCOUT_KEY = app_variables.scout_key

scout_apm.celery.install()

WEBHOOK_HANDLERS = {"bot": process.process_webhook, "challenges": challenges.main}

STATS_HANDLERS = {
    "bot":
        {
            "athlete": process.process_update_stats,
            "all": process.process_update_all_stats
        },
    "challenges":
        {
            "athlete": challenges.update_challenges_stats,
            "all": challenges.update_all_challenges_stats
        }
}


@app.task
@execution_time
def handle_webhook(category, event):
    logging.info("Webhook Event Received | Category: %s | Event: %s", category, event)
    if category in WEBHOOK_HANDLERS:
        WEBHOOK_HANDLERS[category](event)
    else:
        logging.error("Invalid webhook category.")


@app.task
@execution_time
def update_stats(category, athlete_id):
    if athlete_id:
        logging.info("Received request to update stats for %s in %s.", athlete_id, category)
        if category in STATS_HANDLERS:
            STATS_HANDLERS[category]["athlete"](athlete_id)
        else:
            logging.error("Invalid category.")
    else:
        logging.info("Received request to update stats for all the athletes in %s.", category)
        if category in STATS_HANDLERS:
            STATS_HANDLERS[category]["all"]()
        else:
            logging.error("Invalid category.")


@app.task
@execution_time
def challenges_api_hits():
    logging.info("Received request for challenges API hits.")
    challenges.api_hits()


@app.task
@execution_time
def telegram_send_message(message, chat_id=None):
    logging.info("Received request to send message to a user. Chat ID: %s, Message: %s", chat_id, message)
    telegram_resource.send_message(chat_id=chat_id, message=message)


@app.task
@execution_time
def telegram_send_approval_message(message, callback_data):
    logging.info("Received request to send approval message to the admin group. Message: %s | Callback Data: %s",
                 message, callback_data)
    telegram_resource.send_payment_approval_message(message=message, callback_data=callback_data)
