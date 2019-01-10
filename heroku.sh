#!/bin/bash
celery worker -A app.app.celery &
gunicorn app.app:app
