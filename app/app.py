#  -*- encoding: utf-8 -*-


import asyncio
import logging

from flask import request, jsonify
from quart import Quart

from app.commands.process import ProcessStats
from app.common.constants_and_variables import AppVariables, AppConstants

app_variables = AppVariables()
app_constants = AppConstants()

loop = asyncio.get_event_loop()
app = Quart(__name__)
app.config.from_object(__name__)


async def update_stats(athlete_id):
    process_stats = ProcessStats()
    calc_stats = process_stats.process(athlete_id)
    print(calc_stats)


@app.route("/")
async def notify():
    await update_stats(11591902)
    return jsonify(''), 200


@app.route("/stats/<telegram_username>", methods=['POST'])
def stats(telegram_username):
    if request.method == 'POST':
        return telegram_username


@app.route('/webhook', methods=['GET', 'POST'])
def strava_webhook():
    if request.method == 'POST':
        message = request.json
        logging.info("Received webhook event: {event}".format(event=message))

        return jsonify(''), 200

    elif request.method == 'GET':
        hub_challenge = request.args.get('hub.challenge')
        logging.info("Hub Challenge ID: {hub_challenge}".format(hub_challenge=hub_challenge))
        return jsonify({'hub.challenge': hub_challenge}), 200


if __name__ == '__main__' and __package__ is None:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)
    app.run(host=app_variables.app_host, port=app_variables.app_port, debug=app_variables.app_debug)
