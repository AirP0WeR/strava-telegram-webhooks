import os

from celery import Celery

app = Celery()
app.conf.broker_url(os.environ.get('REDIS_URL'))


@app.task
def hello():
    print("Hello")
