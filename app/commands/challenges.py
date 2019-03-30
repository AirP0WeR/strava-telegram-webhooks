#  -*- encoding: utf-8 -*-

import logging
import traceback

import ujson

from app.common.constants_and_variables import AppConstants, AppVariables
from app.common.operations import Operations
from app.resources.athlete import AthleteResource
from app.resources.database import DatabaseResource
from app.resources.iron_cache import IronCacheResource
from app.resources.strava import StravaResource
from app.resources.telegram import TelegramResource


class Challenges(object):

    def __init__(self):
        self.app_constants = AppConstants()
        self.operations = Operations()
        self.strava_resource = StravaResource()
        self.athlete_resource = AthleteResource()
        self.telegram_resource = TelegramResource()
        self.database_resource = DatabaseResource()
        self.calculate_challenges_stats = CalculateChallengesStats()

    def handle_aspect_type_update(self, event, athlete_details):
        athlete_id = event['owner_id']
        if 'authorized' in event['updates'] and event['updates']['authorized'] == "false" and athlete_details:
            if self.database_resource.write_operation(
                    self.app_constants.QUERY_DEACTIVATE_ATHLETE_IN_CHALLENGES.format(athlete_id=athlete_id)):
                message = self.app_constants.MESSAGE_CHALLENGES_DEAUTHORIZE_SUCCESS.format(
                    name=athlete_details['name'],
                    athlete_id=athlete_id)
            else:
                message = self.app_constants.MESSAGE_CHALLENGES_DEAUTHORIZE_FAILURE.format(
                    name=athlete_details['name'],
                    athlete_id=athlete_id)
            self.telegram_resource.shadow_message(message)

    def alert_webhook_event_of_athlete(self, event, athlete_details):
        event_type = "New Activity"
        if event['aspect_type'] == "delete":
            event_type = "Activity Deleted"
        message = self.app_constants.MESSAGE_CHALLENGES_ACTIVITY_ALERT.format(callback_type=event_type,
                                                                              activity_id=event['object_id'],
                                                                              athlete_name=athlete_details['name'])
        self.telegram_resource.shadow_message(message)

    def handle_aspect_type_create(self, event, athlete_details):
        activity_id = event['object_id']
        activity = self.strava_resource.get_strava_activity(athlete_details['athlete_token'], activity_id)
        if activity:
            if self.operations.supported_activities_for_challenges(activity):
                self.calculate_challenges_stats.main(athlete_details)
                self.calculate_challenges_stats.consolidate_even_challenges()
                self.calculate_challenges_stats.consolidate_odd_challenges()
            else:
                message = self.app_constants.MESSAGE_CHALLENGES_UNSUPPORTED_ACTIVITY.format(activity_type=activity.type)
                logging.info(message)
                self.telegram_resource.shadow_message(message)
        else:
            message = "Triggering update challenges stats as something went wrong. Exception: {exception}".format(
                exception=traceback.format_exc())
            logging.error(message)
            self.telegram_resource.shadow_message(message)
            self.calculate_challenges_stats.main(athlete_details)
            self.calculate_challenges_stats.consolidate_even_challenges()
            self.calculate_challenges_stats.consolidate_odd_challenges()

    def update_challenges_stats(self, athlete_id):
        athlete_details = self.athlete_resource.get_athlete_details_in_challenges(athlete_id)
        self.calculate_challenges_stats.main(athlete_details)
        self.calculate_challenges_stats.consolidate_even_challenges()
        self.calculate_challenges_stats.consolidate_odd_challenges()

    def update_all_challenges_stats(self):
        athlete_ids = self.database_resource.read_all_operation(
            self.app_constants.QUERY_GET_ATHLETE_IDS_FROM_CHALLENGES)
        if athlete_ids:
            for athlete_id in athlete_ids:
                athlete_details = self.athlete_resource.get_athlete_details_in_challenges(athlete_id[0])
                if athlete_details:
                    self.calculate_challenges_stats.main(athlete_details)
            self.calculate_challenges_stats.consolidate_even_challenges()
            self.calculate_challenges_stats.consolidate_odd_challenges()

    def main(self, event):
        aspect_type = event['aspect_type']
        athlete_id = event['owner_id']
        athlete_details = self.athlete_resource.get_athlete_details_in_challenges(athlete_id)

        if aspect_type == "update":
            self.handle_aspect_type_update(event, athlete_details)
        else:
            if athlete_details:
                self.alert_webhook_event_of_athlete(event, athlete_details)
                if aspect_type == "create":
                    self.handle_aspect_type_create(event, athlete_details)
                elif aspect_type == "delete":
                    self.calculate_challenges_stats.main(athlete_details)
                    self.calculate_challenges_stats.consolidate_even_challenges()
                    self.calculate_challenges_stats.consolidate_odd_challenges()


class CalculateChallengesStats(object):

    def __init__(self):
        self.app_constants = AppConstants()
        self.app_variables = AppVariables()
        self.operations = Operations()
        self.strava_resource = StravaResource()
        self.telegram_resource = TelegramResource()
        self.database_resource = DatabaseResource()
        self.iron_cache_resource = IronCacheResource()

    def even_challenges(self, athlete_details):
        even_challenges_ride_calendar = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0,
                                         12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0,
                                         21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0,
                                         30: 0, 31: 0}
        even_challenges_rides_count = 0
        even_challenges_total_distance = 0.0
        even_challenges_total_elevation = 0

        even_challenges_stats = {
            '20_20': 0,
            '1000_km': 0.0,
            '10000_meters': 0
        }

        if athlete_details['even_challenges']:
            even_challenges = athlete_details['even_challenges']
            for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                    athlete_details['athlete_token'], self.app_variables.even_challenges_from_date,
                    self.app_variables.even_challenges_to_date):
                if '20_20' in even_challenges:
                    if activity.start_date_local.month == self.app_variables.even_challenges_month and activity.start_date_local.year == self.app_variables.even_challenges_year:
                        even_challenges_ride_calendar[activity.start_date_local.day] += float(activity.distance)
                if '1000_km' in even_challenges:
                    even_challenges_total_distance += float(activity.distance)
                if '10000_meters' in even_challenges:
                    if not self.operations.is_indoor(activity):
                        even_challenges_total_elevation += float(activity.total_elevation_gain)

            if '20_20' in even_challenges:
                for distance in even_challenges_ride_calendar:
                    if even_challenges_ride_calendar[distance] >= 20000.0:
                        even_challenges_rides_count += 1
                even_challenges_stats['20_20'] = even_challenges_rides_count
            if '1000_km' in even_challenges:
                even_challenges_stats['1000_km'] = self.operations.meters_to_kilometers(even_challenges_total_distance)
            if '10000_meters' in even_challenges:
                even_challenges_stats['10000_meters'] = even_challenges_total_elevation

            if self.database_resource.write_operation(
                    self.app_constants.QUERY_UPDATE_EVEN_CHALLENGES_DATA.format(
                        even_challenges_data=ujson.dumps(even_challenges_stats),
                        athlete_id=athlete_details['athlete_id'])):
                self.telegram_resource.shadow_message(
                    "Updated even challenges data for {name}.".format(name=athlete_details['name']))
            else:
                self.telegram_resource.shadow_message(
                    "Failed to update even challenges data for {name}".format(name=athlete_details['name']))

    def odd_challenges(self, athlete_details):
        odd_challenges_ride_calendar = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0,
                                        12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0,
                                        21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0,
                                        30: 0, 31: 0}
        odd_challenges_rides_count = 0
        odd_challenges_total_distance = 0.0
        odd_challenges_total_elevation = 0

        odd_challenges_stats = {
            '20_20': 0,
            '1000_km': 0.0,
            '10000_meters': 0
        }

        if athlete_details['odd_challenges']:
            odd_challenges = athlete_details['odd_challenges']
            for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                    athlete_details['athlete_token'], self.app_variables.odd_challenges_from_date,
                    self.app_variables.odd_challenges_to_date):
                if '20_20' in odd_challenges:
                    if activity.start_date_local.month == self.app_variables.odd_challenges_month and activity.start_date_local.year == self.app_variables.odd_challenges_year:
                        odd_challenges_ride_calendar[activity.start_date_local.day] += float(activity.distance)
                if '1000_km' in odd_challenges:
                    odd_challenges_total_distance += float(activity.distance)
                if '10000_meters' in odd_challenges:
                    if not self.operations.is_indoor(activity):
                        odd_challenges_total_elevation += float(activity.total_elevation_gain)

            if '20_20' in odd_challenges:
                for distance in odd_challenges_ride_calendar:
                    if odd_challenges_ride_calendar[distance] >= 20000.0:
                        odd_challenges_rides_count += 1
                odd_challenges_stats['20_20'] = odd_challenges_rides_count
            if '1000_km' in odd_challenges:
                odd_challenges_stats['1000_km'] = self.operations.meters_to_kilometers(odd_challenges_total_distance)
            if '10000_meters' in odd_challenges:
                odd_challenges_stats['10000_meters'] = odd_challenges_total_elevation

            if self.database_resource.write_operation(
                    self.app_constants.QUERY_UPDATE_ODD_CHALLENGES_DATA.format(
                        odd_challenges_data=ujson.dumps(odd_challenges_stats),
                        athlete_id=athlete_details['athlete_id'])):
                self.telegram_resource.shadow_message(
                    "Updated odd challenges data for {name}.".format(name=athlete_details['name']))
            else:
                self.telegram_resource.shadow_message(
                    "Failed to update odd challenges data for {name}".format(name=athlete_details['name']))

    def consolidate_even_challenges(self):
        even_challenge_twenty_twenty = list()
        even_challenge_thousand_km = list()
        even_challenge_ten_thousand_meters = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_EVEN_CHALLENGES_DATA)
        for result in results:
            name = result[0]
            challenges = result[1]
            challenges_data = result[2]

            if challenges:
                if '20_20' in challenges:
                    even_challenges = {'name': name, 'value': challenges_data['20_20']}
                    even_challenge_twenty_twenty.append(even_challenges)

                if '1000_km' in challenges:
                    even_challenges = {'name': name, 'value': challenges_data['1000_km']}
                    even_challenge_thousand_km.append(even_challenges)

                if '10000_meters' in challenges:
                    even_challenges = {'name': name, 'value': challenges_data['10000_meters']}
                    even_challenge_ten_thousand_meters.append(even_challenges)

        self.iron_cache_resource.put_cache("even_challenges", "20_20", ujson.dumps(even_challenge_twenty_twenty))
        self.iron_cache_resource.put_cache("even_challenges", "1000_km", ujson.dumps(even_challenge_thousand_km))
        self.iron_cache_resource.put_cache("even_challenges", "10000_meters",
                                           ujson.dumps(even_challenge_ten_thousand_meters))

    def consolidate_odd_challenges(self):
        odd_challenge_twenty_twenty = list()
        odd_challenge_thousand_km = list()
        odd_challenge_ten_thousand_meters = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_ODD_CHALLENGES_DATA)
        for result in results:
            name = result[0]
            challenges = result[1]
            challenges_data = result[2]

            if challenges:
                if '20_20' in challenges:
                    odd_challenges = {'name': name, 'value': challenges_data['20_20']}
                    odd_challenge_twenty_twenty.append(odd_challenges)

                if '1000_km' in challenges:
                    odd_challenges = {'name': name, 'value': challenges_data['1000_km']}
                    odd_challenge_thousand_km.append(odd_challenges)

                if '10000_meters' in challenges:
                    odd_challenges = {'name': name, 'value': challenges_data['10000_meters']}
                    odd_challenge_ten_thousand_meters.append(odd_challenges)

        self.iron_cache_resource.put_cache("odd_challenges", "20_20", ujson.dumps(odd_challenge_twenty_twenty))
        self.iron_cache_resource.put_cache("odd_challenges", "1000_km", ujson.dumps(odd_challenge_thousand_km))
        self.iron_cache_resource.put_cache("odd_challenges", "10000_meters",
                                           ujson.dumps(odd_challenge_ten_thousand_meters))

    def main(self, athlete_details):
        self.even_challenges(athlete_details)
        self.odd_challenges(athlete_details)
