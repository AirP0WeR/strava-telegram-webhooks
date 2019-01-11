#  -*- encoding: utf-8 -*-

import logging

from flask import Flask, request, jsonify

from app.commands.process import ProcessStats
from app.common.constants_and_variables import AppVariables, AppConstants
from app.tasks import update_stats

app_variables = AppVariables()
app_constants = AppConstants()

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/stats/<athlete_id>", methods=['POST'])
def stats(athlete_id):
    if request.method == 'POST':
        update_stats.delay(athlete_id)
        return jsonify(''), 200


@app.route("/bikes/<athlete_id>", methods=['POST'])
def get_bikes(athlete_id):
    if request.method == 'POST':
        process_stats = ProcessStats()
        token = {'bikes': process_stats.get_bikes(athlete_id)}
        return jsonify(token), 200


@app.route('/webhook', methods=['GET', 'POST'])
def strava_webhook():
    if request.method == 'POST':
        message = request.json
        logging.info("Received webhook event: {event}".format(event=message))
        update_stats.delay(message['owner_id'])
        return jsonify(''), 200

    elif request.method == 'GET':
        hub_challenge = request.args.get('hub.challenge')
        logging.info("Hub Challenge ID: {hub_challenge}".format(hub_challenge=hub_challenge))
        return jsonify({'hub.challenge': hub_challenge}), 200


if __name__ == '__main__':
    app.run(host=app_variables.app_host, port=int(app_variables.app_port), debug=app_variables.app_debug)
