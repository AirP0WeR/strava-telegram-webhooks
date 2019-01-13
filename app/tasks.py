import logging

from celery import Celery

from app.commands.process import Process
from app.common.constants_and_variables import AppVariables

app_variables = AppVariables()

app = Celery()
app.conf.BROKER_URL = app_variables.redis_url


@app.task
def update_stats(athlete_id):
    logging.info("Received callback to update stats")
    process_stats = Process()
    process_stats.process_update_stats(athlete_id)
    logging.info("Updated stats for: {athlete_id}".format(athlete_id=athlete_id))


@app.task
def update_all_stats():
    logging.info("Received callback to update stats for all the athletes")
    process_stats = Process()
    process_stats.process_update_all_stats()
    logging.info("Updated stats for all the athletes")


@app.task
def update_indoor_ride(athlete_id, activity_id):
    logging.info("Received callback to update indoor ride")
    process_auto_update_indoor_ride = Process()
    process_auto_update_indoor_ride.process_auto_update_indoor_ride(athlete_id, activity_id)
