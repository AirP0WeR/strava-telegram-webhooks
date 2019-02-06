web: gunicorn app.app:app
worker: celery worker -A worker -B app.processor.app -l INFO