#  -*- encoding: utf-8 -*-

import logging
import traceback

import ujson

from app.commands.activity_summary import ActivitySummary
from app.commands.auto_update_indoor_ride import AutoUpdateIndoorRide
from app.commands.calculate import CalculateStats
from app.common.aes_cipher import AESCipher
from app.common.constants_and_variables import AppConstants, AppVariables
from app.common.operations import Operations
from app.resources.athlete import AthleteResource
from app.resources.database import DatabaseResource
from app.resources.iron_cache import IronCacheResource
from app.resources.strava import StravaResource
from app.resources.telegram import TelegramResource


class Process:

    def __init__(self):
        self.bot_constants = AppConstants()
        self.bot_variables = AppVariables()
        self.operations = Operations()
        self.aes_cipher = AESCipher(self.bot_variables.crypt_key_length, self.bot_variables.crypt_key)
        self.telegram_resource = TelegramResource()
        self.database_resource = DatabaseResource()
        self.strava_resource = StravaResource()
        self.athlete_resource = AthleteResource()
        self.iron_cache_resource = IronCacheResource()
        self.auto_update_indoor_ride = AutoUpdateIndoorRide()
        self.activity_summary = ActivitySummary()

    def calculate_stats(self, athlete_details):
        calculate_stats = CalculateStats(athlete_details['athlete_token'])
        calculated_stats = calculate_stats.calculate()
        name = calculated_stats['athlete_name']
        calculated_stats = ujson.dumps(calculated_stats)
        self.database_resource.write_operation(
            self.bot_constants.QUERY_UPDATE_STRAVA_DATA.format(name=name, strava_data=calculated_stats,
                                                               athlete_id=athlete_details['athlete_id']))
        self.iron_cache_resource.put_cache("stats", athlete_details['telegram_username'], calculated_stats)
        self.telegram_resource.send_message(self.bot_constants.MESSAGE_UPDATED_STATS.format(athlete_name=name))
        logging.info("Updated stats for https://www.strava.com/athletes/%s", athlete_details['athlete_id'])

    def process_update_stats(self, athlete_id):
        athlete_details = self.athlete_resource.get_athlete_details(athlete_id)
        if athlete_details:
            self.calculate_stats(athlete_details)
            self.telegram_resource.send_message(chat_id=athlete_details['chat_id'],
                                                message="Updated stats. Click /stats to check.", shadow=False)
        else:
            message = "Old athlete [Athlete](https://www.strava.com/athletes/{athlete_id}). Not registered anymore.".format(
                athlete_id=athlete_id)
            logging.info(message)
            self.telegram_resource.send_message(message)

    def process_update_all_stats(self):
        athlete_ids = self.database_resource.read_all_operation(self.bot_constants.QUERY_FETCH_ALL_ATHLETE_IDS)
        for athlete_id in athlete_ids:
            athlete_details = self.athlete_resource.get_athlete_details(athlete_id[0])
            if athlete_details:
                logging.info("Updating stats for %s", athlete_id[0])
                self.calculate_stats(athlete_details)
        logging.info("Updated stats for all the athletes.")

    def alert_webhook_event_of_athlete(self, event, athlete_details):
        event_type = "New Activity"
        if event['aspect_type'] == "delete":
            event_type = "Activity Deleted"
        message = self.bot_constants.MESSAGE_ACTIVITY_ALERT.format(callback_type=event_type,
                                                                   activity_id=event['object_id'],
                                                                   athlete_name=athlete_details['name'])
        self.telegram_resource.send_message(message)

    def handle_aspect_type_update(self, event, athlete_details):
        athlete_id = event['owner_id']
        if 'authorized' in event['updates'] and event['updates']['authorized'] == "false":
            if athlete_details:
                if self.database_resource.write_operation(
                        self.bot_constants.QUERY_DEACTIVATE_ATHLETE.format(athlete_id=athlete_id)):
                    message = self.bot_constants.MESSAGE_DEAUTHORIZE_SUCCESS.format(name=athlete_details['name'],
                                                                                    athlete_id=athlete_id)
                else:
                    message = self.bot_constants.MESSAGE_DEAUTHORIZE_FAILURE.format(name=athlete_details['name'],
                                                                                    athlete_id=athlete_id)
                self.telegram_resource.send_message(message)

    def handle_aspect_type_create(self, event, athlete_details):
        activity_id = event['object_id']
        object_type = event['object_type']
        activity = self.strava_resource.get_strava_activity(athlete_details['athlete_token'], activity_id)
        if activity:
            if self.operations.supported_activities(activity):
                self.calculate_stats(athlete_details)
                if object_type == "activity":
                    self.auto_update_indoor_ride.main(activity, athlete_details)
                    self.activity_summary.main(activity, athlete_details)
            else:
                message = self.bot_constants.MESSAGE_UNSUPPORTED_ACTIVITY.format(
                    activity_type=activity.type)
                logging.info(message)
                self.telegram_resource.send_message(message)
        else:
            message = "Triggering update stats as something went wrong. Exception: {exception}".format(
                exception=traceback.format_exc())
            logging.error(message)
            self.telegram_resource.send_message(message)
            self.calculate_stats(athlete_details)

    def process_webhook(self, event):
        aspect_type = event['aspect_type']
        athlete_id = event['owner_id']
        activity_id = event['object_id']
        athlete_details = self.athlete_resource.get_athlete_details(athlete_id)

        if aspect_type == "update":
            self.handle_aspect_type_update(event, athlete_details)
        else:
            if athlete_details:
                self.alert_webhook_event_of_athlete(event, athlete_details)
                if aspect_type == "create":
                    self.handle_aspect_type_create(event, athlete_details)
                elif aspect_type == "delete":
                    self.calculate_stats(athlete_details)
            else:
                logging.info(
                    "Old Athlete: [Athlete](https://www.strava.com/athletes/%s) | [Activity](https://www.strava.com/activities/%s)",
                    athlete_id, activity_id)
