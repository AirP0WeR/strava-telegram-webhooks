#  -*- encoding: utf-8 -*-

import json
import logging
import time

import psycopg2
import requests

from app.clients.iron_cache import IronCache
from app.clients.strava import StravaClient
from app.commands.calculate import CalculateStats
from app.common.constants_and_variables import AppConstants, AppVariables
from app.common.operations import Operations
from app.common.shadow_mode import ShadowMode


class Process(object):

    def __init__(self):
        self.bot_constants = AppConstants()
        self.bot_variables = AppVariables()
        self.operations = Operations()
        self.shadow_mode = ShadowMode()
        self.iron_cache = IronCache()

    def refresh_and_update_token(self, athlete_id, refresh_token):
        response = requests.post(self.bot_constants.API_TOKEN_EXCHANGE, data={
            'client_id': int(self.bot_variables.client_id),
            'client_secret': self.bot_variables.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }).json()

        access_info = dict()
        access_info['access_token'] = response['access_token']
        access_info['refresh_token'] = response['refresh_token']
        access_info['expires_at'] = response['expires_at']

        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.bot_constants.QUERY_UPDATE_TOKEN.format(
            access_token=access_info['access_token'],
            refresh_token=access_info['refresh_token'],
            expires_at=access_info['expires_at'],
            athlete_id=athlete_id
        ))
        cursor.close()
        database_connection.commit()
        database_connection.close()

        return response['access_token']

    def get_athlete_details(self, athlete_id):
        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.bot_constants.QUERY_FETCH_TOKEN_NAME_TELEGRAM_NAME.format(athlete_id=athlete_id))
        result = cursor.fetchall()
        cursor.close()
        database_connection.close()
        if len(result) > 0:
            access_token = result[0][0]
            refresh_token = result[0][1]
            expires_at = result[0][2]
            name = result[0][3]
            telegram_username = result[0][4]
            current_time = int(time.time())
            if current_time > expires_at:
                logging.info(
                    "Token has expired | Current Time: {current_time} | Token Expiry Time: {expires_at}".format(
                        current_time=current_time, expires_at=expires_at))
                access_token = self.refresh_and_update_token(athlete_id, refresh_token)
                return access_token, name, telegram_username
            else:
                logging.info(
                    "Token is still valid | Current Time: {current_time} | Token Expiry Time: {expires_at}".format(
                        current_time=current_time, expires_at=expires_at))
                return access_token, name, telegram_username
        else:
            return False, False, False

    def insert_strava_data(self, athlete_id, name, strava_data):
        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.bot_constants.QUERY_UPDATE_STRAVA_DATA.format(name=name,
                                                                          strava_data=strava_data,
                                                                          athlete_id=athlete_id))
        cursor.close()
        database_connection.commit()
        database_connection.close()

    def is_update_indoor_ride(self, athlete_id):
        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.bot_constants.QUERY_FETCH_UPDATE_INDOOR_RIDE.format(athlete_id=athlete_id))
        results = cursor.fetchone()
        cursor.close()
        database_connection.close()

        update_indoor_ride = results[0]
        update_indoor_ride_data = results[1]

        if update_indoor_ride:
            return update_indoor_ride_data
        else:
            return False

    def process_update_stats(self, athlete_id):
        athlete_token, name, telegram_username = self.get_athlete_details(athlete_id)
        if athlete_token:
            calculate_stats = CalculateStats(athlete_token)
            calculated_stats = calculate_stats.calculate()
            name = calculated_stats['athlete_name']
            calculated_stats = json.dumps(calculated_stats)
            self.insert_strava_data(athlete_id, name, calculated_stats)
            self.iron_cache.put(cache="stats", key=telegram_username, value=calculated_stats)
            self.shadow_mode.send_message(self.bot_constants.MESSAGE_UPDATED_STATS.format(athlete_name=name))
            logging.info("Updated stats for https://www.strava.com/athletes/{athlete_id}".format(athlete_id=athlete_id))
        else:
            message = "Old athlete (https://www.strava.com/athletes/{athlete_id}). Not registered anymore.".format(
                athlete_id=athlete_id)
            logging.info(message)
            self.shadow_mode.send_message(message)

    def process_update_all_stats(self):
        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.bot_constants.QUERY_FETCH_ALL_ATHLETE_IDS)
        athlete_ids = cursor.fetchall()
        cursor.close()
        database_connection.close()

        for athlete_id in athlete_ids:
            athlete_token, name, telegram_username = self.get_athlete_details(athlete_id[0])
            if athlete_token:
                logging.info("Updating stats for {athlete_id}".format(athlete_id=athlete_id[0]))
                calculate_stats = CalculateStats(athlete_token)
                calculated_stats = calculate_stats.calculate()
                name = calculated_stats['athlete_name']
                calculated_stats = json.dumps(calculated_stats)
                self.insert_strava_data(athlete_id[0], name, calculated_stats)
                self.iron_cache.put(cache="stats", key=telegram_username, value=calculated_stats)
                self.shadow_mode.send_message(self.bot_constants.MESSAGE_UPDATED_STATS.format(athlete_name=name))

    def process_auto_update_indoor_ride(self, event, athlete_token):
        athlete_id = event['owner_id']
        update_indoor_ride_data = self.is_update_indoor_ride(athlete_id)
        if update_indoor_ride_data:
            activity_id = event['object_id']
            strava_client_with_token = StravaClient().get_client_with_token(athlete_token)
            activity = strava_client_with_token.get_activity(activity_id)

            if self.operations.is_activity_a_ride(activity) and self.operations.is_indoor(activity):

                if update_indoor_ride_data['name'] == 'Automatic':
                    activity_hour = activity.start_date_local.hour
                    if 3 <= activity_hour <= 11:
                        update_indoor_ride_data['name'] = "Morning Ride"
                    elif 12 <= activity_hour <= 15:
                        update_indoor_ride_data['name'] = "Afternoon Ride"
                    elif 16 <= activity_hour <= 18:
                        update_indoor_ride_data['name'] = "Evening Ride"
                    elif (19 <= activity_hour <= 23) or (0 <= activity_hour <= 2):
                        update_indoor_ride_data['name'] = "Night Ride"

                strava_client_with_token.update_activity(activity_id=activity_id,
                                                         name=update_indoor_ride_data['name'],
                                                         gear_id=update_indoor_ride_data['gear_id'])
                logging.info("Updated indoor ride")
                self.shadow_mode.send_message(self.bot_constants.MESSAGE_UPDATED_INDOOR_RIDE)
            else:
                logging.info("Not a indoor ride")
        else:
            logging.info("Auto update indoor ride is not enabled")

    def process_webhook(self, event):
        if event['aspect_type'] != "update":
            aspect_type = event['aspect_type']
            athlete_id = event['owner_id']
            object_type = event['object_type']
            activity_id = event['object_id']
            athlete_token, name, telegram_username = self.get_athlete_details(athlete_id)
            if athlete_token:
                callback_type = "New Activity"
                if aspect_type == "delete":
                    callback_type = "Activity Deleted"
                self.shadow_mode.send_message(
                    self.bot_constants.MESSAGE_ACTIVITY_ALERT.format(callback_type=callback_type,
                                                                     activity_id=activity_id, athlete_name=name))
                if aspect_type == "create" and object_type == "activity":
                    self.process_auto_update_indoor_ride(event, athlete_token)
                calculate_stats = CalculateStats(athlete_token)
                calculated_stats = calculate_stats.calculate()
                name = calculated_stats['athlete_name']
                calculated_stats = json.dumps(calculated_stats)
                self.insert_strava_data(athlete_id, name, calculated_stats)
                self.iron_cache.put(cache="stats", key=telegram_username, value=calculated_stats)
                self.shadow_mode.send_message(self.bot_constants.MESSAGE_UPDATED_STATS.format(athlete_name=name))
                logging.info(
                    "Updated stats for https://www.strava.com/athletes/{athlete_id}".format(athlete_id=athlete_id))
            else:
                message = self.bot_constants.MESSAGE_OLD_ATHLETE.format(athlete_id=athlete_id, activity_id=activity_id)
                logging.info(message)
                self.shadow_mode.send_message(message)
