#  -*- encoding: utf-8 -*-

import logging
import traceback

from flask import Flask, request, jsonify
from scout_apm.flask import ScoutApm

from app.common.constants_and_variables import AppVariables, AppConstants
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
def token_exchange(code):
    if request.method == 'POST':
        logging.info("Received request for token exchange with code: {code}".format(code=code))
        access_info = strava_resource.token_exchange(code)
        if access_info:
            return jsonify(access_info), 200
        else:
            return jsonify(''), 500


@app.route("/token/get/<athlete_id>", methods=['GET'])
def get_token(athlete_id):
    if request.method == 'GET':
        logging.info("Received request to get token for athlete: {athlete_id}".format(athlete_id=athlete_id))
        athlete_token = athlete_resource.get_token(athlete_id)
        if athlete_token:
            return jsonify(athlete_token), 200
        else:
            return jsonify(''), 500


@app.route("/athlete/exists/<athlete_id>", methods=['GET'])
def athlete_exists(athlete_id):
    if request.method == 'GET':
        logging.info("Received request to check if athlete https://www.strava.com/athletes/{athlete_id} exists.".format(
            athlete_id=athlete_id))
        exists = athlete_resource.exists(athlete_id)
        if exists:
            return jsonify(''), 200
        else:
            return jsonify(''), 404


@app.route("/database/write", methods=['POST'])
def database_write():
    if request.method == 'POST' and request.json and "query" in request.json:
        query = request.json["query"]
        logging.info("Received request to write to the database: {query}".format(query=query))
        result = database_resource.write_operation(query)
        if result:
            return jsonify(''), 200
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
