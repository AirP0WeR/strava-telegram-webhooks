#  -*- encoding: utf-8 -*-

from flask import Flask, request, jsonify

from app.common.constants_and_variables import AppVariables, AppConstants
from app.common.shadow_mode import ShadowMode
from app.tasks import update_stats, update_indoor_ride, update_all_stats

app_variables = AppVariables()
app_constants = AppConstants()
shadow_mode = ShadowMode()

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/stats/<athlete_id>", methods=['POST'])
def stats(athlete_id):
    if request.method == 'POST':
        update_stats.delay(athlete_id)
        return jsonify(''), 200


@app.route("/stats/all", methods=['POST'])
def stats_for_all():
    if request.method == 'POST':
        update_all_stats.delay()
        return jsonify(''), 200


@app.route('/webhook', methods=['GET', 'POST'])
def strava_webhook():
    if request.method == 'POST':
        message = request.json
        update_stats.delay(message['owner_id'])
        if message['aspect_type'] == "create" and message['object_type'] == "activity":
            shadow_mode.send_message(app_constants.MESSAGE_NEW_ACTIVITY.format(activity_id=message['object_id']))
            update_indoor_ride.delay(message['owner_id'], message['object_id'])
        return jsonify(''), 200

    elif request.method == 'GET':
        hub_challenge = request.args.get('hub.challenge')
        return jsonify({'hub.challenge': hub_challenge}), 200


if __name__ == '__main__':
    app.run(host=app_variables.app_host, port=int(app_variables.app_port), debug=app_variables.app_debug)
