#  -*- encoding: utf-8 -*-

import os


class AppConstants(object):
    QUERY_FETCH_TOKEN = "select access_token, refresh_token, expires_at from strava_telegram_bot where athlete_id={athlete_id}"
    QUERY_UPDATE_TOKEN = "UPDATE strava_telegram_bot SET access_token='{access_token}', refresh_token='{refresh_token}', expires_at={expires_at}, updated=now() where athlete_id={athlete_id}"
    QUERY_UPDATE_STRAVA_DATA = "UPDATE strava_telegram_bot SET strava_data='{strava_data}', updated=now() WHERE athlete_id={athlete_id}"
    API_TOKEN_EXCHANGE = 'https://www.strava.com/oauth/token'


class AppVariables(object):
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    app_port = os.environ.get('APP_PORT')
    database_url = os.environ.get('DATABASE_URL')
    app_debug = os.environ.get('APP_DEBUG')
    app_host = os.environ.get('APP_HOST')
    redis_url = os.environ.get('REDIS_URL')
