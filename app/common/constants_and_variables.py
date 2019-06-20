#  -*- encoding: utf-8 -*-
import json
import os


class AppConstants:
    QUERY_FETCH_ATHLETE_DETAILS = "select telegram_username, name, access_token, refresh_token, expires_at, strava_data, update_indoor_ride, update_indoor_ride_data, chat_id, enable_activity_summary from strava_telegram_bot where active=true and athlete_id={athlete_id}"
    QUERY_FETCH_ATHLETE_DETAILS_BY_TELEGRAM_USERNAME = "select athlete_id, name, access_token, refresh_token, expires_at, strava_data, update_indoor_ride, update_indoor_ride_data, chat_id, enable_activity_summary from strava_telegram_bot where active=true and LOWER(telegram_username)=LOWER('{telegram_username}')"
    QUERY_UPDATE_TOKEN = "UPDATE strava_telegram_bot SET access_token='{access_token}', refresh_token='{refresh_token}', expires_at={expires_at}, updated=now() where athlete_id={athlete_id}"
    QUERY_UPDATE_STRAVA_DATA = "UPDATE strava_telegram_bot SET name='{name}', strava_data='{strava_data}', updated=now() WHERE athlete_id={athlete_id}"
    QUERY_FETCH_ALL_ATHLETE_IDS = "select athlete_id from strava_telegram_bot where active=true"
    QUERY_DEACTIVATE_ATHLETE = "UPDATE strava_telegram_bot SET active=false, strava_data=null, update_indoor_ride=false, update_indoor_ride_data=null, chat_id=null, enable_activity_summary=false, updated=now() WHERE athlete_id={athlete_id}"
    QUERY_ATHLETE_EXISTS = "select count(*) from strava_telegram_bot where athlete_id={athlete_id}"
    QUERY_GET_ATHLETE_ID = "select athlete_id from strava_telegram_bot where LOWER(telegram_username)=LOWER('{telegram_username}') and active=TRUE"
    QUERY_GET_STRAVA_DATA = "select strava_data from strava_telegram_bot where LOWER(telegram_username)=LOWER('{telegram_username}')"
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

    QUERY_CREATE_TABLE_CHALLENGES = '''create table strava_challenges(
                id serial NOT NULL,
                athlete_id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL,
                access_token VARCHAR NOT NULL,
                refresh_token VARCHAR NOT NULL,
                expires_at INTEGER NOT NULL,
                even_challenges json DEFAULT NULL,
                even_challenges_data json DEFAULT NULL,
                odd_challenges json DEFAULT NULL,
                odd_challenges_data json DEFAULT NULL,
                created timestamp NOT NULL,
                updated timestamp default current_timestamp NOT NULL
                );'''

    QUERY_FETCH_ATHLETE_DETAILS_IN_CHALLENGES = "select name, access_token, refresh_token, expires_at, even_challenges, even_challenges_data, odd_challenges, odd_challenges_data, bosch_even_challenges, bosch_even_challenges_data, bosch_odd_challenges, bosch_odd_challenges_data from strava_challenges where athlete_id={athlete_id}"
    QUERY_GET_CHALLENGE_DETAILS_FROM_CHALLENGES = "select {column_name} from strava_challenges where athlete_id={athlete_id}"
    QUERY_APPROVE_PAYMENT_IN_CHALLENGES = "UPDATE strava_challenges SET {column_name}='{challenge_details}', updated=now() where athlete_id={athlete_id}"
    QUERY_UPDATE_TOKEN_IN_CHALLENGES = "UPDATE strava_challenges SET access_token='{access_token}', refresh_token='{refresh_token}', expires_at={expires_at}, updated=now() where athlete_id={athlete_id}"
    QUERY_DELETE_ATHLETE_FROM_CHALLENGES = "DELETE from strava_challenges WHERE athlete_id={athlete_id}"
    QUERY_UPDATE_EVEN_CHALLENGES_DATA = "UPDATE strava_challenges SET even_challenges_data='{even_challenges_data}', updated=now() where athlete_id={athlete_id}"
    QUERY_UPDATE_ODD_CHALLENGES_DATA = "UPDATE strava_challenges SET odd_challenges_data='{odd_challenges_data}', updated=now() where athlete_id={athlete_id}"
    QUERY_UPDATE_BOSCH_EVEN_CHALLENGES_DATA = "UPDATE strava_challenges SET bosch_even_challenges_data='{bosch_even_challenges_data}', updated=now() where athlete_id={athlete_id}"
    QUERY_GET_ATHLETE_IDS_FROM_CHALLENGES = "select athlete_id from strava_challenges"
    QUERY_GET_EVEN_CHALLENGES_DATA = "select name, even_challenges, even_challenges_data from strava_challenges"
    QUERY_GET_ODD_CHALLENGES_DATA = "select name, odd_challenges, odd_challenges_data from strava_challenges"
    QUERY_GET_BOSCH_EVEN_CHALLENGES_DATA = "select name, bosch_even_challenges, bosch_even_challenges_data from strava_challenges"
    QUERY_GET_ATHLETES_EVEN_CHALLENGES = "select athlete_id, name, even_challenges from strava_challenges order by created"
    QUERY_GET_ATHLETES_EVEN_BOSCH_CHALLENGES = "select athlete_id, name, bosch_even_challenges from strava_challenges order by created"
    QUERY_GET_ATHLETES_ODD_BOSCH_CHALLENGES = "select athlete_id, name, bosch_odd_challenges from strava_challenges order by created"
    QUERY_GET_ATHLETES_ODD_CHALLENGES = "select athlete_id, name, odd_challenges from strava_challenges order by created"

    API_TOKEN_EXCHANGE = 'https://www.strava.com/oauth/token'
    API_TELEGRAM_SEND_MESSAGE = "https://api.telegram.org/bot{bot_token}/sendMessage"

    MESSAGE_ACTIVITY_ALERT = "[{callback_type}](https://www.strava.com/activities/{activity_id}) by `{athlete_name}`."
    MESSAGE_CHALLENGES_ACTIVITY_ALERT = "[{callback_type}](https://www.strava.com/activities/{activity_id}) by `{athlete_name}` who has registered for the Challenges."
    MESSAGE_UNSUPPORTED_ACTIVITY = "{activity_type} is not supported yet. Ignoring update stats."
    MESSAGE_CHALLENGES_UNSUPPORTED_ACTIVITY = "{activity_type} is not part of the Challenges. Ignoring.."
    MESSAGE_UPDATED_INDOOR_RIDE = "Updated your Indoor Ride with the below configuration:\n"
    MESSAGE_UPDATED_STATS = "Updated stats for `{athlete_name}`."
    MESSAGE_DEAUTHORIZE_SUCCESS = "[{name}](https://www.strava.com/athletes/{athlete_id}) deauthorized Strava App."
    MESSAGE_CHALLENGES_DEAUTHORIZE_SUCCESS = "[{name}](https://www.strava.com/athletes/{athlete_id}) deauthorized Cadence90 Challenges App."
    MESSAGE_DEAUTHORIZE_FAILURE = "Failed to deactivate [{name}](https://www.strava.com/athletes/{athlete_id})."
    MESSAGE_CHALLENGES_DEAUTHORIZE_FAILURE = "Failed to deactivate [{name}](https://www.strava.com/athletes/{athlete_id}) in Cadence90 Challenges."


class AppVariables:
    crypt_key_length = int(os.environ.get('CRYPT_KEY_LENGTH'))
    crypt_key = os.environ.get('CRYPT_KEY')
    client_id = int(os.environ.get('CLIENT_ID'))
    challenges_client_id = int(os.environ.get('CHALLENGES_CLIENT_ID'))
    client_secret = os.environ.get('CLIENT_SECRET')
    challenges_client_secret = os.environ.get('CHALLENGES_CLIENT_SECRET')
    app_port = os.environ.get('APP_PORT')
    database_url = os.environ.get('DATABASE_URL')
    app_debug = os.environ.get('APP_DEBUG')
    app_host = os.environ.get('APP_HOST')
    redis_url = os.environ.get('REDIS_URL')
    shadow_mode = os.environ.get('SHADOW_MODE')
    shadow_mode_chat_id = os.environ.get('SHADOW_MODE_CHAT_ID')
    approval_group_chat_id = os.environ.get('APPROVAL_GROUP_CHAT_ID')
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    iron_cache_project_id = os.environ.get('IRON_CACHE_PROJECT_ID')
    iron_cache_token = os.environ.get('IRON_CACHE_TOKEN')
    scout_monitor = os.environ.get('SCOUT_MONITOR')
    scout_key = os.environ.get('SCOUT_KEY')
    scout_name = os.environ.get('SCOUT_NAME')
    logging_level = os.environ.get('LOGGING_LEVEL')
    even_challenges_year = int(os.environ.get('EVEN_CHALLENGES_YEAR'))
    even_challenges_month = int(os.environ.get('EVEN_CHALLENGES_MONTH'))
    even_challenges_from_date = os.environ.get('EVEN_CHALLENGES_FROM_DATE')
    even_challenges_to_date = os.environ.get('EVEN_CHALLENGES_TO_DATE')
    odd_challenges_year = int(os.environ.get('ODD_CHALLENGES_YEAR'))
    odd_challenges_month = int(os.environ.get('ODD_CHALLENGES_MONTH'))
    odd_challenges_from_date = os.environ.get('ODD_CHALLENGES_FROM_DATE')
    odd_challenges_to_date = os.environ.get('ODD_CHALLENGES_TO_DATE')
    location_gps = json.loads(os.environ.get('LOCATION_GPS'))
    location_threshold = float(os.environ.get('LOCATION_THRESHOLD'))
    timezone = os.environ.get('TZ')
