from celery import Celery

from app.common.constants_and_variables import AppVariables

app_variables = AppVariables()

app = Celery()
app.config_from_object("celery_settings")

@app.task
def hello():
    print("Hello")
