#  -*- encoding: utf-8 -*-

import os


class AppConstants(object):
    QUERY_FETCH_TOKEN_NAME_TELEGRAM_NAME = "select access_token, refresh_token, expires_at, name, telegram_username from strava_telegram_bot where athlete_id={athlete_id}"
    QUERY_UPDATE_TOKEN = "UPDATE strava_telegram_bot SET access_token='{access_token}', refresh_token='{refresh_token}', expires_at={expires_at}, updated=now() where athlete_id={athlete_id}"
    QUERY_UPDATE_STRAVA_DATA = "UPDATE strava_telegram_bot SET name='{name}', strava_data='{strava_data}', updated=now() WHERE athlete_id={athlete_id}"
    QUERY_FETCH_UPDATE_INDOOR_RIDE = "select update_indoor_ride, update_indoor_ride_data from strava_telegram_bot where athlete_id={athlete_id}"
    QUERY_FETCH_ALL_ATHLETE_IDS = "select athlete_id from strava_telegram_bot"

    API_TOKEN_EXCHANGE = 'https://www.strava.com/oauth/token'
    API_TELEGRAM_SEND_MESSAGE = "https://api.telegram.org/bot{bot_token}/sendMessage"

    MESSAGE_NEW_ACTIVITY = "New Activity: [{activity_name}](https://www.strava.com/activities/{activity_id}) by {athlete_name}."
    MESSAGE_UPDATED_INDOOR_RIDE = "Indoor Ride has been updated."
    MESSAGE_UPDATED_STATS = "Updated stats for {athlete_name}."


class AppVariables(object):
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    app_port = os.environ.get('APP_PORT')
    database_url = os.environ.get('DATABASE_URL')
    app_debug = os.environ.get('APP_DEBUG')
    app_host = os.environ.get('APP_HOST')
    redis_url = os.environ.get('REDIS_URL')
    shadow_mode = os.environ.get('SHADOW_MODE')
    shadow_mode_chat_id = os.environ.get('SHADOW_MODE_CHAT_ID')
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    iron_cache_project_id = os.environ.get('IRON_CACHE_PROJECT_ID')
    iron_cache_token = os.environ.get('IRON_CACHE_TOKEN')
