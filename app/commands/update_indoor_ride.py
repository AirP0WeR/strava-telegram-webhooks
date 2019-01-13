#  -*- encoding: utf-8 -*-

from os import sys, path

import psycopg2

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from app.clients.strava import StravaClient
from app.common.constants_and_variables import AppConstants, AppVariables
from app.common.operations import Operations


class UpdateIndoorRide(object):

    def __init__(self):
        self.bot_constants = AppConstants()
        self.bot_variables = AppVariables()
        self.operations = Operations()
        self.strava_client = StravaClient()

    def is_update_indoor_ride(self, athlete_id):
        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(
            "select update_indoor_ride, update_indoor_ride_data from strava_telegram_bot where athlete_id={athlete_id}".format(
                athlete_id=athlete_id))
        results = cursor.fetchone()
        cursor.close()
        database_connection.close()

        update_indoor_ride = results[0]
        update_indoor_ride_data = results[1]

        if update_indoor_ride:
            return update_indoor_ride_data
        else:
            return False

    def process(self, athlete_id, activity_id):
        athlete_token = self.strava_client.get_athlete_token(athlete_id)
        strava_client_with_token = StravaClient().get_client_with_token(athlete_token)
        activity = strava_client_with_token.get_activity(activity_id)
        if self.operations.is_indoor(activity):
            update_indoor_ride_data = self.is_update_indoor_ride(athlete_id)
            if update_indoor_ride_data:
                strava_client_with_token.update_activity(activity_id=activity_id, name=update_indoor_ride_data['name'],
                                                         gear_id=update_indoor_ride_data['gear_id'])
