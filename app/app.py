#  -*- encoding: utf-8 -*-

import logging
import traceback

from flask import Flask, request, jsonify
from scout_apm.flask import ScoutApm

from app.common.constants_and_variables import AppVariables, AppConstants
from app.common.execution_time import execution_time
from app.processor import update_stats, handle_webhook, update_all_stats, telegram_shadow_message, telegram_send_message
from app.resources.athlete import AthleteResource
from app.resources.database import DatabaseResource
from app.resources.strava import StravaResource

app_variables = AppVariables()
app_constants = AppConstants()
strava_resource = StravaResource()
athlete_resource = AthleteResource()
database_resource = DatabaseResource()

app = Flask(__name__)
app.config.from_object(__name__)

ScoutApm(app)

app.config['SCOUT_MONITOR'] = app_variables.scout_monitor
app.config['SCOUT_KEY'] = app_variables.scout_key
app.config['SCOUT_NAME'] = app_variables.scout_name

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.os.environ.get('LOGGING_LEVEL'))
logger = logging.getLogger(__name__)


@app.route('/webhook', methods=['GET', 'POST'])
def strava_webhook():
    try:
        if request.method == 'POST':
            event = request.json
            handle_webhook.delay(event)
            return jsonify(''), 200
        elif request.method == 'GET':
            hub_challenge = request.args.get('hub.challenge')
            return jsonify({'hub.challenge': hub_challenge}), 200
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        telegram_shadow_message.delay(message)


@app.route("/stats/<athlete_id>", methods=['POST'])
def stats(athlete_id):
    if request.method == 'POST':
        update_stats.delay(athlete_id)
        return jsonify('Accepted'), 200


@app.route("/stats/all", methods=['POST'])
def stats_for_all():
    if request.method == 'POST':
        update_all_stats.delay()
        return jsonify('Accepted'), 200


@app.route("/token/exchange/<code>", methods=['POST'])
@execution_time
def token_exchange(code):
    if request.method == 'POST':
        logging.info("Received request for token exchange with code: {code}".format(code=code))
        access_info = strava_resource.token_exchange(code)
        if access_info:
            return jsonify(access_info), 200
        else:
            return jsonify(''), 500


@app.route("/athlete/exists/<athlete_id>", methods=['GET'])
@execution_time
def athlete_exists(athlete_id):
    if request.method == 'GET':
        logging.info("Received request to check if athlete https://www.strava.com/athletes/{athlete_id} exists.".format(
            athlete_id=athlete_id))
        exists = athlete_resource.exists(athlete_id)
        if exists:
            return jsonify(''), 200
        else:
            return jsonify(''), 404


@app.route("/athlete/get/<athlete_id>", methods=['GET'])
@execution_time
def get_athlete(athlete_id):
    if request.method == 'GET':
        logging.info("Received request to get athlete https://www.strava.com/athletes/{athlete_id}".format(
            athlete_id=athlete_id))
        result = athlete_resource.get_athlete_details(athlete_id)
        if result:
            return jsonify(result), 200
        else:
            return jsonify(''), 500


@app.route("/athlete/stats/<telegram_username>", methods=['GET'])
@execution_time
def get_stats(telegram_username):
    if request.method == 'GET':
        logging.info(
            "Received request to get stats for {telegram_username}".format(telegram_username=telegram_username))
        result = athlete_resource.get_stats(telegram_username)
        if result:
            return jsonify(result), 200
        else:
            return jsonify(''), 500


@app.route("/strava/bikes/<token>", methods=['GET'])
@execution_time
def get_bikes_list(token):
    if request.method == 'GET':
        logging.info("Received request to get bikes list")
        bikes = strava_resource.get_bikes_list(token)
        if bikes:
            return jsonify(bikes), 200
        else:
            return jsonify(''), 500


@app.route("/strava/gear/name/<token>/<gear_id>", methods=['GET'])
@execution_time
def get_gear_name(token, gear_id):
    if request.method == 'GET':
        logging.info("Received request to get gear name. Gear ID {gear_id}".format(gear_id=gear_id))
        gear_name = strava_resource.get_gear_name(token, gear_id)
        if gear_name:
            return jsonify(gear_name), 200
        else:
            return jsonify(''), 500


@app.route("/athlete/get_by_telegram_username/<telegram_username>", methods=['GET'])
@execution_time
def get_athlete_by_telegram_username(telegram_username):
    if request.method == 'GET':
        logging.info("Received request to get athlete details for {telegram_username}".format(
            telegram_username=telegram_username))
        result = athlete_resource.get_athlete_details_by_telegram_username(telegram_username)
        if result:
            return jsonify(result), 200
        else:
            return jsonify(''), 500


@app.route("/athlete/athlete_id/<telegram_username>", methods=['GET'])
@execution_time
def get_athlete_id(telegram_username):
    if request.method == 'GET':
        logging.info(
            "Received request to get Athlete ID for {telegram_username}.".format(telegram_username=telegram_username))
        athlete_id = athlete_resource.get_athlete_id(telegram_username)
        if athlete_id:
            return jsonify(athlete_id), 200
        else:
            return jsonify(''), 404


@app.route("/database/write", methods=['POST'])
@execution_time
def database_write():
    if request.method == 'POST' and request.json and "query" in request.json:
        query = request.json["query"]
        logging.info("Received request to write to the database: {query}".format(query=query))
        result = database_resource.write_operation(query)
        if result:
            return jsonify(''), 200
        else:
            return jsonify(''), 500


@app.route("/database/read", methods=['GET'])
@execution_time
def database_read():
    if request.method == 'GET' and request.json and "query" in request.json:
        query = request.json["query"]
        logging.info("Received request to fetch one from the database: {query}".format(query=query))
        result = database_resource.read_operation(query)
        if result:
            return jsonify(result), 200
        else:
            return jsonify(''), 500


@app.route("/database/read/all", methods=['GET'])
@execution_time
def database_read_all():
    if request.method == 'GET' and request.json and "query" in request.json:
        query = request.json["query"]
        logging.info("Received request to fetch all from the database: {query}".format(query=query))
        result = database_resource.read_all_operation(query)
        if result:
            return jsonify(result), 200
        else:
            return jsonify(''), 500


@app.route("/telegram/send_message", methods=['POST'])
def send_message():
    if request.method == 'POST' and request.json and "chat_id" in request.json and "message" in request.json:
        chat_id = request.json["chat_id"]
        message = request.json["message"]
        telegram_send_message.delay(chat_id, message)
        return jsonify('Accepted'), 200


@app.route("/telegram/shadow_message", methods=['POST'])
def shadow_message():
    if request.method == 'POST' and request.json and "message" in request.json:
        message = request.json["message"]
        telegram_shadow_message.delay(message)
        return jsonify('Accepted'), 200


@app.route("/healthcheck")
def healthcheck():
    return jsonify('OK'), 200


if __name__ == '__main__':
    app.run(host=app_variables.app_host, port=int(app_variables.app_port), debug=app_variables.app_debug)
