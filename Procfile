web: gunicorn app.app:app
worker: celery worker -A app.processor.app -B -l INFO