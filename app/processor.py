#  -*- encoding: utf-8 -*-

import logging
import traceback

import scout_apm.celery
from celery import Celery
from celery.schedules import crontab

from app.commands.process import Process
from app.common.constants_and_variables import AppVariables
from app.common.shadow_mode import ShadowMode

app_variables = AppVariables()
shadow_mode = ShadowMode()

app = Celery()
app.conf.BROKER_URL = app_variables.redis_url
app.conf.BROKER_POOL_LIMIT = 0
app.conf.SCOUT_MONITOR = app_variables.scout_monitor
app.conf.SCOUT_NAME = app_variables.scout_name
app.conf.SCOUT_KEY = app_variables.scout_key
app.conf.CELERY_TIMEZONE = app_variables.timezone

scout_apm.celery.install()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        # crontab(hour=0, minute=5, day_of_month=1),
        crontab(minute=1),
        update_all_stats.s()
    )


@app.task
def handle_webhook(event):
    try:
        logging.info("Webhook Event Received: {event}".format(event=event))
        process = Process()
        process.process_webhook(event)
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        shadow_mode.send_message(message)


@app.task
def update_stats(athlete_id):
    try:
        logging.info("Received callback to update stats for https://www.strava.com/athletes/{athlete_id}".format(
            athlete_id=athlete_id))
        process_stats = Process()
        process_stats.process_update_stats(athlete_id)
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        shadow_mode.send_message(message)


@app.task
def update_all_stats():
    try:
        logging.info("Received callback to update stats for all the athletes")
        process_stats = Process()
        process_stats.process_update_all_stats()
        logging.info("Updated stats for all the athletes")
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        shadow_mode.send_message(message)
