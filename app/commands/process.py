#  -*- encoding: utf-8 -*-

import json
import logging
import time

import requests
from stravalib import unithelper

from app.clients.database import DatabaseClient
from app.clients.iron_cache import IronCache
from app.clients.strava import StravaClient
from app.clients.telegram import TelegramClient
from app.commands.calculate import CalculateStats
from app.common.aes_cipher import AESCipher
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
        self.aes_cipher = AESCipher(self.bot_variables.crypt_key_length, self.bot_variables.crypt_key)
        self.telegram_client = TelegramClient()
        self.database_client = DatabaseClient()

    def refresh_and_update_token(self, athlete_id, refresh_token):
        response = requests.post(self.bot_constants.API_TOKEN_EXCHANGE, data={
            'client_id': int(self.bot_variables.client_id),
            'client_secret': self.bot_variables.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }).json()

        self.database_client.write_operation(self.bot_constants.QUERY_UPDATE_TOKEN.format(
            access_token=self.aes_cipher.encrypt(response['access_token']),
            refresh_token=self.aes_cipher.encrypt(response['refresh_token']),
            expires_at=response['expires_at'],
            athlete_id=athlete_id
        ))

        return response['access_token']

    def get_athlete_details(self, athlete_id):
        athlete_details = {'athlete_token': None, 'name': None, 'telegram_username': None}
        result = self.database_client.read_operation(
            self.bot_constants.QUERY_FETCH_TOKEN_NAME_TELEGRAM_NAME.format(athlete_id=athlete_id))
        if len(result) > 0:
            athlete_details['athlete_token'] = self.aes_cipher.decrypt(result[0])
            refresh_token = self.aes_cipher.decrypt(result[1])
            expires_at = result[2]
            athlete_details['name'] = result[3]
            athlete_details['telegram_username'] = result[4]

            if int(time.time()) > expires_at:
                athlete_details['athlete_token'] = self.refresh_and_update_token(athlete_id, refresh_token)

        return athlete_details

    def is_update_indoor_ride(self, athlete_id):
        results = self.database_client.read_operation(
            self.bot_constants.QUERY_FETCH_UPDATE_INDOOR_RIDE.format(athlete_id=athlete_id))
        update_indoor_ride = results[0]
        update_indoor_ride_data = results[1]
        chat_id = results[2]

        if update_indoor_ride:
            return update_indoor_ride_data, chat_id
        else:
            return False

    def is_activity_summary(self, athlete_id):
        results = self.database_client.read_operation(
            self.bot_constants.QUERY_ACTIVITY_SUMMARY.format(athlete_id=athlete_id))
        enable_activity_summary = results[0]
        chat_id = results[1]

        if enable_activity_summary:
            return chat_id
        else:
            return False

    def calculate_stats(self, athlete_token, athlete_id, telegram_username):
        calculate_stats = CalculateStats(athlete_token)
        calculated_stats = calculate_stats.calculate()
        name = calculated_stats['athlete_name']
        calculated_stats = json.dumps(calculated_stats)
        self.database_client.write_operation(
            self.bot_constants.QUERY_UPDATE_STRAVA_DATA.format(name=name, strava_data=calculated_stats,
                                                               athlete_id=athlete_id))
        self.iron_cache.put(cache="stats", key=telegram_username, value=calculated_stats)
        self.shadow_mode.send_message(self.bot_constants.MESSAGE_UPDATED_STATS.format(athlete_name=name))
        logging.info("Updated stats for https://www.strava.com/athletes/{athlete_id}".format(athlete_id=athlete_id))

    def process_update_stats(self, athlete_id):
        athlete_details = self.get_athlete_details(athlete_id)
        if athlete_details['athlete_token']:
            self.calculate_stats(athlete_details['athlete_token'], athlete_id, athlete_details['telegram_username'])
        else:
            message = "Old athlete (https://www.strava.com/athletes/{athlete_id}). Not registered anymore.".format(
                athlete_id=athlete_id)
            logging.info(message)
            self.shadow_mode.send_message(message)

    def process_update_all_stats(self):
        athlete_ids = self.database_client.read_all_operation(self.bot_constants.QUERY_FETCH_ALL_ATHLETE_IDS)
        for athlete_id in athlete_ids:
            athlete_details = self.get_athlete_details(athlete_id[0])
            if athlete_details['athlete_token']:
                logging.info("Updating stats for {athlete_id}".format(athlete_id=athlete_id[0]))
                self.calculate_stats(athlete_details['athlete_token'], athlete_id[0],
                                     athlete_details['telegram_username'])

    def process_auto_update_indoor_ride(self, activity, athlete_token, athlete_id, activity_id):
        update_indoor_ride_data, chat_id = self.is_update_indoor_ride(athlete_id)
        if update_indoor_ride_data:
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

                strava_client = StravaClient().get_client(athlete_token)
                strava_client.update_activity(activity_id=activity_id, name=update_indoor_ride_data['name'],
                                              gear_id=update_indoor_ride_data['gear_id'])
                logging.info("Updated indoor ride")
                configured_data = self.bot_constants.MESSAGE_UPDATED_INDOOR_RIDE
                if update_indoor_ride_data['name']:
                    configured_data += "\nActivity Name: {activity_name}".format(
                        activity_name=update_indoor_ride_data['name'])
                if update_indoor_ride_data['gear_id']:
                    bike_name = strava_client.get_gear(gear_id=update_indoor_ride_data['gear_id']).name
                    configured_data += "\nBike: {bike_name}".format(bike_name=bike_name)

                message = configured_data
                self.telegram_client.send_message(chat_id=chat_id, message=message)
                self.shadow_mode.send_message(message)
            else:
                logging.info("Not an indoor ride")
        else:
            logging.info("Auto update indoor ride is not enabled")

    def process_activity_summary(self, activity, name, athlete_id):
        chat_id = self.is_activity_summary(athlete_id)
        if chat_id:
            if self.operations.supported_activities(activity):
                activity_summary = "*New Activity Summary*:\n\n" \
                                   "Athlete Name: {athlete_name}\n" \
                                   "Activity: [{activity_name}](https://www.strava.com/activities/{activity_id})\n" \
                                   "Activity Date: {activity_date}\n" \
                                   "Activity Type: {activity_type}\n\n" \
                                   "Distance: {distance} km\n" \
                                   "Moving Time: {moving_time}\n" \
                                   "Elapsed Time: {elapsed_time}\n" \
                                   "Avg Speed: {avg_speed}\n" \
                                   "Max Speed: {max_speed}\n" \
                                   "Calories: {calories}\n".format(
                    athlete_name=name,
                    activity_name=activity.name,
                    activity_id=activity.id,
                    activity_type=activity.type,
                    activity_date=activity.start_date_local,
                    distance=self.operations.meters_to_kilometers(float(activity.distance)),
                    moving_time=self.operations.seconds_to_human_readable(
                        unithelper.timedelta_to_seconds(activity.moving_time)),
                    elapsed_time=self.operations.seconds_to_human_readable(
                        unithelper.timedelta_to_seconds(activity.elapsed_time)),
                    avg_speed=unithelper.kilometers_per_hour(activity.average_speed),
                    max_speed=unithelper.kilometers_per_hour(activity.max_speed),
                    calories=self.operations.remove_decimal_point(activity.calories))

                if not self.operations.is_indoor(activity):
                    activity_summary += "\nElevation Gain: {elevation_gain} meters".format(
                        elevation_gain=self.operations.remove_decimal_point(activity.total_elevation_gain))

                if activity.average_cadence:
                    activity_summary += "\nAvg Cadence: {avg_cadence}".format(
                        avg_cadence=self.operations.remove_decimal_point(activity.average_cadence))

                if activity.has_heartrate:
                    activity_summary += "\nAvg HR: {avg_hr} bpm\nMax HR: {max_hr} bpm".format(
                        avg_hr=self.operations.remove_decimal_point(activity.average_heartrate),
                        max_hr=self.operations.remove_decimal_point(activity.max_heartrate))

                if self.operations.is_activity_a_ride(activity) and activity.device_watts:
                    activity_summary += "\nAvg Watts: {avg_watts}\nMax Watts: {max_watts}".format(
                        avg_watts=activity.average_watts, max_watts=activity.max_watts)

                activity_summary += "\n\n_Click_ /stats _to check your updated stats_"
            else:
                activity_summary = "*New Activity*:\n\n" \
                                   "Athlete Name: {athlete_name}\n" \
                                   "Activity: [{activity_name}](https://www.strava.com/activities/{activity_id})\n" \
                                   "Activity Date: {activity_date}\n" \
                                   "Activity Type: {activity_type}\n\n" \
                                   "{activity_type} is not yet supported for Activity Summary.".format(
                    athlete_name=name,
                    activity_name=activity.name,
                    activity_id=activity.id,
                    activity_type=activity.type,
                    activity_date=activity.start_date_local)

            self.telegram_client.send_message(chat_id=chat_id, message=activity_summary)
            self.shadow_mode.send_message(activity_summary)

    def process_webhook(self, event):
        if event['aspect_type'] != "update":
            aspect_type = event['aspect_type']
            athlete_id = event['owner_id']
            object_type = event['object_type']
            activity_id = event['object_id']

            athlete_details = self.get_athlete_details(athlete_id)
            if athlete_details['athlete_token']:
                callback_type = "New Activity"
                if aspect_type == "delete":
                    callback_type = "Activity Deleted"
                self.shadow_mode.send_message(
                    self.bot_constants.MESSAGE_ACTIVITY_ALERT.format(callback_type=callback_type,
                                                                     activity_id=activity_id,
                                                                     athlete_name=athlete_details['name']))

                if aspect_type == "create":
                    strava_client_with_token = StravaClient().get_client(athlete_details['athlete_token'])
                    activity = strava_client_with_token.get_activity(activity_id)

                    if self.operations.supported_activities(activity):
                        self.calculate_stats(athlete_details['athlete_token'], athlete_id,
                                             athlete_details['telegram_username'])
                        if object_type == "activity":
                            self.process_auto_update_indoor_ride(activity, athlete_details['athlete_token'], athlete_id,
                                                                 activity_id)
                            self.process_activity_summary(activity, athlete_details['name'], athlete_id)
                    else:
                        self.shadow_mode.send_message(
                            self.bot_constants.MESSAGE_UNSUPPORTED_ACTIVITY.format(activity_type=activity.type))

                elif aspect_type == "delete":
                    self.calculate_stats(athlete_details['athlete_token'], athlete_id,
                                         athlete_details['telegram_username'])
            else:
                message = self.bot_constants.MESSAGE_OLD_ATHLETE.format(athlete_id=athlete_id, activity_id=activity_id)
                logging.info(message)
                self.shadow_mode.send_message(message)
