web: gunicorn app.app:app
worker: celery worker -A app.tasks.app -l INFO