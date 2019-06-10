#  -*- encoding: utf-8 -*-

import logging
import traceback

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


@app.task
@execution_time
def handle_webhook(name, event):
    logging.info("Webhook Event Received. Name: %s | Event: %s", name, event)
    if name in WEBHOOK_HANDLERS:
        WEBHOOK_HANDLERS[name](event)
    else:
        logging.error("Invalid webhook name")


@app.task
@execution_time
def update_stats(athlete_id):
    try:
        logging.info("Received request to update stats for https://www.strava.com/athletes/%s.", athlete_id)
        process.process_update_stats(athlete_id)
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        telegram_resource.shadow_message(message)


@app.task
@execution_time
def update_all_stats():
    try:
        logging.info("Received request to update stats for all the athletes.")
        process.process_update_all_stats()
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        telegram_resource.shadow_message(message)


@app.task
@execution_time
def update_challenges_stats(athlete_id):
    try:
        logging.info(
            "Received request to update challenges stats for https://www.strava.com/athletes/%s.", athlete_id)
        challenges.update_challenges_stats(athlete_id)
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        telegram_resource.shadow_message(message)


@app.task
@execution_time
def update_all_challenges_stats():
    try:
        logging.info("Received request to update all challenges stats.")
        challenges.update_all_challenges_stats()
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        telegram_resource.shadow_message(message)


@app.task
@execution_time
def challenges_api_hits():
    try:
        logging.info("Received request for challenges API hits.")
        challenges.api_hits()
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        telegram_resource.shadow_message(message)


@app.task
@execution_time
def telegram_send_message(chat_id, message):
    logging.info(
        "Received request to send message to a user. Chat ID: %s, Message: %s", chat_id, message)
    telegram_resource.send_message(chat_id, message)


@app.task
@execution_time
def telegram_shadow_message(message):
    logging.info("Received request to shadow message to the admin group. Message: %s", message)
    telegram_resource.shadow_message(message)
