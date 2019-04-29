#  -*- encoding: utf-8 -*-

import logging
import operator
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
        self.iron_cache_resource = IronCacheResource()

    def handle_aspect_type_update(self, event, athlete_details):
        athlete_id = event['owner_id']
        if 'authorized' in event['updates'] and event['updates']['authorized'] == "false" and athlete_details:
            if self.database_resource.write_operation(
                    self.app_constants.QUERY_DELETE_ATHLETE_FROM_CHALLENGES.format(athlete_id=athlete_id)):
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
                self.calculate_challenges_stats.consolidate_even_challenges_result()
                self.calculate_challenges_stats.consolidate_odd_challenges_result()
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
            self.calculate_challenges_stats.consolidate_even_challenges_result()
            self.calculate_challenges_stats.consolidate_odd_challenges_result()

    def update_challenges_stats(self, athlete_id):
        athlete_details = self.athlete_resource.get_athlete_details_in_challenges(athlete_id)
        self.calculate_challenges_stats.main(athlete_details)
        self.calculate_challenges_stats.consolidate_even_challenges_result()
        self.calculate_challenges_stats.consolidate_odd_challenges_result()

    def update_all_challenges_stats(self):
        athlete_ids = self.database_resource.read_all_operation(
            self.app_constants.QUERY_GET_ATHLETE_IDS_FROM_CHALLENGES)
        if athlete_ids:
            for athlete_id in athlete_ids:
                athlete_details = self.athlete_resource.get_athlete_details_in_challenges(athlete_id[0])
                if athlete_details:
                    self.calculate_challenges_stats.main(athlete_details)
            self.calculate_challenges_stats.consolidate_even_challenges_result()
            self.calculate_challenges_stats.consolidate_odd_challenges_result()

    def page_hits(self):
        hits = self.iron_cache_resource.get_int_cache(cache="challenges_hits", key="hits")
        if hits:
            self.iron_cache_resource.put_cache(cache="challenges_hits", key="hits", value=hits + 1)
            challenges_hits = hits + 1
        else:
            self.iron_cache_resource.put_cache(cache="challenges_hits", key="hits", value=1)
            challenges_hits = 1

        self.telegram_resource.shadow_message("Challenges Page Hits: {hits}".format(hits=challenges_hits))

    def challenges_even_athletes_list(self):
        messages = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_ATHLETES_EVEN_CHALLENGES)

        twenty_twenty = "20-20:\n\n"
        twenty_twenty_sl_no = 1
        thousand_km = "1,000 km:\n\n"
        thousand_km_sl_no = 1
        ten_thousand_meters = "10,000 meters:\n\n"
        ten_thousand_meters_sl_no = 1
        total_count = 0

        for result in results:
            athlete_id = result[0]
            name = result[1]
            challenges = result[2]

            if challenges:
                if '20_20' in challenges:
                    twenty_twenty += "{sl_no}. [{name}](https://www.strava.com/athletes/{athlete_id})\n".format(
                        sl_no=twenty_twenty_sl_no, name=name, athlete_id=athlete_id)
                    twenty_twenty_sl_no += 1

                if '1000_km' in challenges:
                    thousand_km += "{sl_no}. [{name}](https://www.strava.com/athletes/{athlete_id})\n".format(
                        sl_no=thousand_km_sl_no, name=name, athlete_id=athlete_id)
                    thousand_km_sl_no += 1

                if '10000_meters' in challenges:
                    ten_thousand_meters += "{sl_no}. [{name}](https://www.strava.com/athletes/{athlete_id})\n".format(
                        sl_no=ten_thousand_meters_sl_no, name=name, athlete_id=athlete_id)
                    ten_thousand_meters_sl_no += 1

                total_count += 1

        total = "Total athletes registered for even month's challenges: {total}".format(total=total_count)

        messages.append(twenty_twenty)
        messages.append(thousand_km)
        messages.append(ten_thousand_meters)
        messages.append(total)

        return messages if messages != [] else False

    def challenges_odd_athletes_list(self):
        messages = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_ATHLETES_ODD_CHALLENGES)

        twenty_twenty = "20-20:\n\n"
        twenty_twenty_sl_no = 1
        thousand_km = "1,000 km:\n\n"
        thousand_km_sl_no = 1
        ten_thousand_meters = "10,000 meters:\n\n"
        ten_thousand_meters_sl_no = 1
        total_count = 0

        for result in results:
            athlete_id = result[0]
            name = result[1]
            challenges = result[2]

            if challenges:
                if '20_20' in challenges:
                    twenty_twenty += "{sl_no}. [{name}](https://www.strava.com/athletes/{athlete_id})\n".format(
                        sl_no=twenty_twenty_sl_no, name=name, athlete_id=athlete_id)
                    twenty_twenty_sl_no += 1

                if '1000_km' in challenges:
                    thousand_km += "{sl_no}. [{name}](https://www.strava.com/athletes/{athlete_id})\n".format(
                        sl_no=thousand_km_sl_no, name=name, athlete_id=athlete_id)
                    thousand_km_sl_no += 1

                if '10000_meters' in challenges:
                    ten_thousand_meters += "{sl_no}. [{name}](https://www.strava.com/athletes/{athlete_id})\n".format(
                        sl_no=ten_thousand_meters_sl_no, name=name, athlete_id=athlete_id)
                    ten_thousand_meters_sl_no += 1

                total_count += 1

        total = "Total athletes registered for odd month's challenges: {total}".format(total=total_count)

        messages.append(twenty_twenty)
        messages.append(thousand_km)
        messages.append(ten_thousand_meters)
        messages.append(total)

        return messages if messages != [] else False

    def main(self, event):
        aspect_type = event['aspect_type']
        athlete_id = event['owner_id']
        athlete_details = self.athlete_resource.get_athlete_details_in_challenges(athlete_id)
        if not athlete_details['bosch_even_challenges']:  # TODO Remove this code
            if aspect_type == "update":
                self.handle_aspect_type_update(event, athlete_details)
            else:
                if athlete_details:
                    self.alert_webhook_event_of_athlete(event, athlete_details)
                    if aspect_type == "create":
                        self.handle_aspect_type_create(event, athlete_details)
                    elif aspect_type == "delete":
                        self.calculate_challenges_stats.main(athlete_details)
                        self.calculate_challenges_stats.consolidate_even_challenges_result()
                        self.calculate_challenges_stats.consolidate_odd_challenges_result()


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
                logging.info(
                    "Type: {activity_type} | Month: {activity_month} | Year: {activity_year} | Day: {activity_day} | Distance: {activity_distance} | Total Elevation Gain: {total_elevation_gain}".format(
                        activity_type=activity.type, activity_month=activity.start_date_local.month,
                        activity_year=activity.start_date_local.year, activity_day=activity.start_date_local.day,
                        activity_distance=float(activity.distance),
                        total_elevation_gain=float(activity.total_elevation_gain)))
                if self.operations.supported_activities_for_challenges(
                        activity) and activity.start_date_local.month == self.app_variables.even_challenges_month and activity.start_date_local.year == self.app_variables.even_challenges_year:
                    if '20_20' in even_challenges:
                        even_challenges_ride_calendar[activity.start_date_local.day] += float(activity.distance)
                    if '1000_km' in even_challenges:
                        even_challenges_total_distance += float(activity.distance)
                    if '10000_meters' in even_challenges:
                        if not self.operations.is_indoor(activity):
                            even_challenges_total_elevation += float(activity.total_elevation_gain)

            logging.info(
                "Even Ride Calendar: {even_challenges_ride_calendar} | Even Rides Count : {even_challenges_rides_count}| Even Total Distance: {even_challenges_total_distance} | Even Total Elevation: {even_challenges_total_elevation}".format(
                    even_challenges_ride_calendar=even_challenges_ride_calendar,
                    even_challenges_rides_count=even_challenges_rides_count,
                    even_challenges_total_distance=even_challenges_total_distance,
                    even_challenges_total_elevation=even_challenges_total_elevation))

            if '20_20' in even_challenges:
                for distance in even_challenges_ride_calendar:
                    if even_challenges_ride_calendar[distance] >= 20000.0:
                        even_challenges_rides_count += 1
                even_challenges_stats['20_20'] = even_challenges_rides_count
            if '1000_km' in even_challenges:
                even_challenges_stats['1000_km'] = self.operations.meters_to_kilometers(even_challenges_total_distance)
            if '10000_meters' in even_challenges:
                even_challenges_stats['10000_meters'] = self.operations.remove_decimal_point(
                    even_challenges_total_elevation)

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
                if self.operations.supported_activities_for_challenges(
                        activity) and activity.start_date_local.month == self.app_variables.even_challenges_month and activity.start_date_local.year == self.app_variables.even_challenges_year:
                    if '20_20' in odd_challenges:
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
                odd_challenges_stats['10000_meters'] = self.operations.remove_decimal_point(
                    odd_challenges_total_elevation)

            if self.database_resource.write_operation(
                    self.app_constants.QUERY_UPDATE_ODD_CHALLENGES_DATA.format(
                        odd_challenges_data=ujson.dumps(odd_challenges_stats),
                        athlete_id=athlete_details['athlete_id'])):
                self.telegram_resource.shadow_message(
                    "Updated odd challenges data for {name}.".format(name=athlete_details['name']))
            else:
                self.telegram_resource.shadow_message(
                    "Failed to update odd challenges data for {name}".format(name=athlete_details['name']))

    def consolidate_even_challenges_result(self):
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
                    even_challenge_twenty_twenty.append({'name': name, 'value': challenges_data['20_20']})
                if '1000_km' in challenges:
                    even_challenge_thousand_km.append({'name': name, 'value': challenges_data['1000_km']})
                if '10000_meters' in challenges:
                    even_challenge_ten_thousand_meters.append({'name': name, 'value': challenges_data['10000_meters']})

        even_challenge_twenty_twenty_temp = sorted(even_challenge_twenty_twenty, key=operator.itemgetter('value'),
                                                   reverse=True)
        even_challenge_thousand_km_temp = sorted(even_challenge_thousand_km, key=operator.itemgetter('value'),
                                                 reverse=True)
        even_challenge_ten_thousand_meters_temp = sorted(even_challenge_ten_thousand_meters,
                                                         key=operator.itemgetter('value'), reverse=True)

        even_challenge_twenty_twenty_sorted = list()
        rank = 1
        for athlete in even_challenge_twenty_twenty_temp:
            even_challenge_twenty_twenty_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        even_challenge_thousand_km_sorted = list()
        rank = 1
        for athlete in even_challenge_thousand_km_temp:
            even_challenge_thousand_km_sorted.append({'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        even_challenge_ten_thousand_meters_sorted = list()
        rank = 1
        for athlete in even_challenge_ten_thousand_meters_temp:
            even_challenge_ten_thousand_meters_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        self.iron_cache_resource.put_cache("even_challenges_result", "20_20",
                                           ujson.dumps(even_challenge_twenty_twenty_sorted))
        self.iron_cache_resource.put_cache("even_challenges_result", "1000_km",
                                           ujson.dumps(even_challenge_thousand_km_sorted))
        self.iron_cache_resource.put_cache("even_challenges_result", "10000_meters",
                                           ujson.dumps(even_challenge_ten_thousand_meters_sorted))
        self.telegram_resource.shadow_message("Updated cache for even challenges.")

    def consolidate_odd_challenges_result(self):
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
                    odd_challenge_twenty_twenty.append({'name': name, 'value': challenges_data['20_20']})
                if '1000_km' in challenges:
                    odd_challenge_thousand_km.append({'name': name, 'value': challenges_data['1000_km']})
                if '10000_meters' in challenges:
                    odd_challenge_ten_thousand_meters.append({'name': name, 'value': challenges_data['10000_meters']})

        odd_challenge_twenty_twenty_temp = sorted(odd_challenge_twenty_twenty, key=operator.itemgetter('value'),
                                                  reverse=True)
        odd_challenge_thousand_km_temp = sorted(odd_challenge_thousand_km, key=operator.itemgetter('value'),
                                                reverse=True)
        odd_challenge_ten_thousand_meters_temp = sorted(odd_challenge_ten_thousand_meters,
                                                        key=operator.itemgetter('value'), reverse=True)

        odd_challenge_twenty_twenty_sorted = list()
        rank = 1
        for athlete in odd_challenge_twenty_twenty_temp:
            odd_challenge_twenty_twenty_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        odd_challenge_thousand_km_sorted = list()
        rank = 1
        for athlete in odd_challenge_thousand_km_temp:
            odd_challenge_thousand_km_sorted.append({'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        odd_challenge_ten_thousand_meters_sorted = list()
        rank = 1
        for athlete in odd_challenge_ten_thousand_meters_temp:
            odd_challenge_ten_thousand_meters_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        self.iron_cache_resource.put_cache("odd_challenges_result", "20_20",
                                           ujson.dumps(odd_challenge_twenty_twenty_sorted))
        self.iron_cache_resource.put_cache("odd_challenges_result", "1000_km",
                                           ujson.dumps(odd_challenge_thousand_km_sorted))
        self.iron_cache_resource.put_cache("odd_challenges_result", "10000_meters",
                                           ujson.dumps(odd_challenge_ten_thousand_meters_sorted))
        self.telegram_resource.shadow_message("Updated cache for odd challenges.")

    def main(self, athlete_details):
        self.even_challenges(athlete_details)
        self.odd_challenges(athlete_details)
