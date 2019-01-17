#  -*- encoding: utf-8 -*-

import logging
import traceback

import scout_apm.celery
from celery import Celery

from app.commands.process import Process
from app.common.constants_and_variables import AppVariables
from app.common.shadow_mode import ShadowMode

app_variables = AppVariables()
shadow_mode = ShadowMode()

app = Celery()
app.conf.BROKER_URL = app_variables.redis_url
app.conf.SCOUT_MONITOR = app_variables.scout_monitor
app.conf.SCOUT_NAME = app_variables.scout_name
app.conf.SCOUT_KEY = app_variables.scout_key

scout_apm.celery.install()


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


@app.task
def update_indoor_ride(athlete_id, activity_id):
    try:
        logging.info("Received callback to update indoor ride")
        process_auto_update_indoor_ride = Process()
        process_auto_update_indoor_ride.process_auto_update_indoor_ride(athlete_id, activity_id)
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        shadow_mode.send_message(message)
