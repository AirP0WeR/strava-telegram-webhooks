import logging

from celery import Celery

from app.commands.process import ProcessStats
from app.common.constants_and_variables import AppVariables

app_variables = AppVariables()

app = Celery()
app.conf.BROKER_URL = app_variables.redis_url


@app.task
def update_stats(athlete_id):
    process_stats = ProcessStats()
    process_stats.process(athlete_id)
    logging.info("Updated stats for: {athlete_id}".format(athlete_id=athlete_id))