from celery import Celery

from app.common.constants_and_variables import AppVariables

app_variables = AppVariables()

app = Celery()
app.conf.BROKER_URL = app_variables.redis_url


@app.task
def hello():
    print("Hello")
