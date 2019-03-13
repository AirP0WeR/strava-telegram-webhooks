#  -*- encoding: utf-8 -*-

import os


class AppConstants(object):
    QUERY_FETCH_ATHLETE_DETAILS = "select telegram_username, name, access_token, refresh_token, expires_at, strava_data, update_indoor_ride, update_indoor_ride_data, chat_id, enable_activity_summary from strava_telegram_bot where active=true and athlete_id={athlete_id}"
    QUERY_FETCH_ATHLETE_DETAILS_BY_TELEGRAM_USERNAME = "select athlete_id, name, access_token, refresh_token, expires_at, strava_data, update_indoor_ride, update_indoor_ride_data, chat_id, enable_activity_summary from strava_telegram_bot where active=true and telegram_username='{telegram_username}'"
    QUERY_UPDATE_TOKEN = "UPDATE strava_telegram_bot SET access_token='{access_token}', refresh_token='{refresh_token}', expires_at={expires_at}, updated=now() where athlete_id={athlete_id}"
    QUERY_UPDATE_STRAVA_DATA = "UPDATE strava_telegram_bot SET name='{name}', strava_data='{strava_data}', updated=now() WHERE athlete_id={athlete_id}"
    QUERY_FETCH_ALL_ATHLETE_IDS = "select athlete_id from strava_telegram_bot where active=true"
    QUERY_DEACTIVATE_ATHLETE = "UPDATE strava_telegram_bot SET active=false, strava_data=null, update_indoor_ride=false, update_indoor_ride_data=null, chat_id=null, enable_activity_summary=false, updated=now() WHERE athlete_id={athlete_id}"
    QUERY_ATHLETE_EXISTS = "select count(*) from strava_telegram_bot where athlete_id={athlete_id}"
    QUERY_GET_ATHLETE_ID = "select athlete_id from strava_telegram_bot where telegram_username='{telegram_username}' and active=TRUE"
    QUERY_GET_STRAVA_DATA = "select strava_data from strava_telegram_bot where telegram_username='{telegram_username}'"
    QUERY_ACTIVITY_SUMMARY_ENABLE = "UPDATE strava_telegram_bot SET enable_activity_summary=True, chat_id='{chat_id}' where athlete_id={athlete_id}"
    QUERY_ACTIVATE_ACTIVE_FLAG_ATHLETE = "UPDATE strava_telegram_bot SET active=true where athlete_id={athlete_id}"
    QUERY_DEACTIVATE_ACTIVE_FLAG_ATHLETE = "UPDATE strava_telegram_bot SET active=false where athlete_id={athlete_id}"
    QUERY_UPDATE_CHAT_ID = "UPDATE strava_telegram_bot SET chat_id='{chat_id}' where athlete_id={athlete_id}"
    QUERY_ACTIVITY_SUMMARY_DISABLE = "UPDATE strava_telegram_bot SET enable_activity_summary=False where athlete_id={athlete_id}"
    QUERY_UPDATE_INDOOR_RIDE_DISABLE = "UPDATE strava_telegram_bot SET update_indoor_ride=False, update_indoor_ride_data=NULL where athlete_id={athlete_id}"
    QUERY_CREATE_TABLE = '''create table strava_telegram_bot(
            id serial NOT NULL,
            athlete_id INTEGER PRIMARY KEY,
            telegram_username VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            access_token VARCHAR NOT NULL,
            refresh_token VARCHAR NOT NULL,
            expires_at INTEGER NOT NULL,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            strava_data json DEFAULT NULL,
            update_indoor_ride BOOLEAN NOT NULL DEFAULT FALSE,
            update_indoor_ride_data json DEFAULT NULL,
            chat_id VARCHAR DEFAULT NULL,
            enable_activity_summary BOOLEAN NOT NULL DEFAULT TRUE,
            created timestamp NOT NULL,
            updated timestamp default current_timestamp NOT NULL
            );'''

    API_TOKEN_EXCHANGE = 'https://www.strava.com/oauth/token'
    API_TELEGRAM_SEND_MESSAGE = "https://api.telegram.org/bot{bot_token}/sendMessage"

    MESSAGE_ACTIVITY_ALERT = "[{callback_type}](https://www.strava.com/activities/{activity_id}) by `{athlete_name}`."
    MESSAGE_UNSUPPORTED_ACTIVITY = "{activity_type} is not supported yet. Ignoring update stats."
    MESSAGE_OLD_ATHLETE = "Old Athlete: [Athlete](https://www.strava.com/athletes/{athlete_id}) | [Activity](https://www.strava.com/activities/{activity_id})"
    MESSAGE_UPDATED_INDOOR_RIDE = "Updated your Indoor Ride with the below configuration:\n"
    MESSAGE_UPDATED_STATS = "Updated stats for `{athlete_name}`."
    MESSAGE_DEAUTHORIZE_SUCCESS = "[{name}](https://www.strava.com/athletes/{athlete_id}) deauthorized Strava App."
    MESSAGE_DEAUTHORIZE_FAILURE = "Failed to deactivate [{name}](https://www.strava.com/athletes/{athlete_id})."


class AppVariables(object):
    crypt_key_length = int(os.environ.get('CRYPT_KEY_LENGTH'))
    crypt_key = os.environ.get('CRYPT_KEY')
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
    scout_monitor = os.environ.get('SCOUT_MONITOR')
    scout_key = os.environ.get('SCOUT_KEY')
    scout_name = os.environ.get('SCOUT_NAME')
    logging_level = os.environ.get('LOGGING_LEVEL')
