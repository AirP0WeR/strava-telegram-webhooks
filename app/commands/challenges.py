#  -*- encoding: utf-8 -*-
import logging
import operator
import traceback
from collections import defaultdict
from math import radians, sin, cos, asin, sqrt

import ujson
from stravalib import unithelper

from app.commands.tok_odd_month import ToKOddMonth
from app.common.constants_and_variables import AppConstants, AppVariables
from app.common.operations import Operations
from app.resources.athlete import AthleteResource
from app.resources.database import DatabaseResource
from app.resources.iron_cache import IronCacheResource
from app.resources.strava import StravaResource
from app.resources.telegram import TelegramResource


class Challenges:

    def __init__(self):
        self.app_constants = AppConstants()
        self.operations = Operations()
        self.strava_resource = StravaResource()
        self.athlete_resource = AthleteResource()
        self.telegram_resource = TelegramResource()
        self.database_resource = DatabaseResource()
        self.calculate_challenges_stats = CalculateChallengesStats()
        self.iron_cache_resource = IronCacheResource()
        self.tok_odd_challenges = ToKOddMonth()

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
            self.calculate_challenges_stats.consolidate_even_challenges_result()
            self.calculate_challenges_stats.consolidate_odd_challenges_result()
            self.calculate_challenges_stats.consolidate_bosch_even_challenges_result()
            self.calculate_challenges_stats.consolidate_bosch_odd_challenges_result()
            self.tok_odd_challenges.consolidate_tok_odd_challenges_result()
            self.telegram_resource.send_message(message)

    def alert_webhook_event_of_athlete(self, event, athlete_details):
        event_type = "New Activity"
        if event['aspect_type'] == "delete":
            event_type = "Activity Deleted"
        message = self.app_constants.MESSAGE_CHALLENGES_ACTIVITY_ALERT.format(callback_type=event_type,
                                                                              activity_id=event['object_id'],
                                                                              athlete_name=athlete_details['name'])
        self.telegram_resource.send_message(message)

    def handle_aspect_type_create(self, event, athlete_details):
        activity_id = event['object_id']
        activity = self.strava_resource.get_strava_activity(athlete_details['athlete_token'], activity_id)
        if activity:
            if self.operations.supported_activities_for_challenges(activity):
                self.calculate_challenges_stats.main(athlete_details)
            else:
                message = self.app_constants.MESSAGE_CHALLENGES_UNSUPPORTED_ACTIVITY.format(activity_type=activity.type)
                logging.info(message)
                self.telegram_resource.send_message(message)
        else:
            message = "Triggering update challenges stats as something went wrong. Exception: {exception}".format(
                exception=traceback.format_exc())
            logging.error(message)
            self.telegram_resource.send_message(message)
            self.calculate_challenges_stats.main(athlete_details)

    def update_challenges_stats(self, athlete_id):
        athlete_details = self.athlete_resource.get_athlete_details_in_challenges(athlete_id)
        self.calculate_challenges_stats.main(athlete_details)

    def update_all_challenges_stats(self):
        athlete_ids = self.database_resource.read_all_operation(
            self.app_constants.QUERY_GET_ATHLETE_IDS_FROM_CHALLENGES)
        if athlete_ids:
            for athlete_id in athlete_ids:
                athlete_details = self.athlete_resource.get_athlete_details_in_challenges(athlete_id[0])
                if athlete_details:
                    if athlete_details['even_challenges']:
                        self.calculate_challenges_stats.even_challenges(athlete_details)
                    if athlete_details['odd_challenges']:
                        self.calculate_challenges_stats.odd_challenges(athlete_details)
                    if athlete_details['bosch_even_challenges']:
                        self.calculate_challenges_stats.bosch_even_challenges(athlete_details)
                    if athlete_details['bosch_odd_challenges']:
                        self.calculate_challenges_stats.bosch_odd_challenges(athlete_details)
                    if athlete_details['tok_odd_challenges']:
                        self.tok_odd_challenges.tok_odd_challenges(athlete_details)
            self.calculate_challenges_stats.consolidate_even_challenges_result()
            self.calculate_challenges_stats.consolidate_odd_challenges_result()
            self.calculate_challenges_stats.consolidate_bosch_even_challenges_result()
            self.calculate_challenges_stats.consolidate_bosch_odd_challenges_result()
            self.tok_odd_challenges.consolidate_tok_odd_challenges_result()

    def api_hits(self):
        hits = self.iron_cache_resource.get_int_cache(cache="challenges_hits", key="hits")
        if hits:
            self.iron_cache_resource.put_cache(cache="challenges_hits", key="hits", value=hits + 1)
            challenges_hits = hits + 1
        else:
            self.iron_cache_resource.put_cache(cache="challenges_hits", key="hits", value=1)
            challenges_hits = 1

        self.telegram_resource.send_message("Challenges API Hits: {hits}".format(hits=challenges_hits))

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

    def challenges_bosch_even_athletes_list(self):
        messages = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_ATHLETES_EVEN_BOSCH_CHALLENGES)
        if results:
            for result in results:
                athlete_id = result[0]
                name = result[1]
                details = result[2]
                messages.append({'name': name,
                                 'location': details['location'],
                                 'ntid': details['ntid'],
                                 'email': details['email'],
                                 'phone': details['phone'],
                                 'athlete_id': athlete_id,
                                 'strava': "https://www.strava.com/athletes/{}".format(athlete_id),
                                 'CycleToWork Rides': True if 'c2w_rides' in details['id'] else False,
                                 'CycleToWork Distance': True if 'c2w_distance' in details['id'] else False,
                                 '2km x 30 (only for Woman riders)': True if '2x30' in details['id'] else False,
                                 '40min x 30rides': True if '40x30' in details['id'] else False,
                                 'How far can you go': True if 'distance' in details['id'] else False})

        return messages if messages != [] else False

    def challenges_bosch_odd_athletes_list(self):
        messages = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_ATHLETES_ODD_BOSCH_CHALLENGES)
        if results:
            for result in results:
                athlete_id = result[0]
                name = result[1]
                details = result[2]
                messages.append({'name': name,
                                 'location': details['location'],
                                 'ntid': details['ntid'],
                                 'email': details['email'],
                                 'phone': details['phone'],
                                 'athlete_id': athlete_id,
                                 'strava': "https://www.strava.com/athletes/{}".format(athlete_id),
                                 'CycleToWork Rides': True if 'c2w_rides' in details['id'] else False,
                                 'CycleToWork Distance': True if 'c2w_distance' in details['id'] else False,
                                 '2km x 30 (only for Woman riders)': True if '2x30' in details['id'] else False,
                                 '40min x 30rides': True if '40x30' in details['id'] else False,
                                 'How far can you go': True if 'distance' in details['id'] else False})

        return messages if messages != [] else False

    def challenges_odd_athletes_list(self):
        registered_athletes = list()
        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_ATHLETES_ODD_CHALLENGES)
        sl_no = 1
        for result in results:
            cadence90_odd_challenges = result[2]
            if cadence90_odd_challenges and cadence90_odd_challenges['payment']:
                registered_athletes.append({'rank': sl_no, 'name': result[1], 'value': 0})
                sl_no += 1

        if len(registered_athletes) == 0:
            registered_athletes.append({'rank': '', 'name': '', 'value': ''})

        return registered_athletes

    @staticmethod
    def dummy_function():
        pass

    def get_challenges_result(self, company, month, challenge):
        challenges_result = False

        companies = ['cadence90', 'bosch', 'tok']
        months = ['odd', 'even']
        challenges = ['leaderboard', 'c2w', '6_km', '30_min', 'distance', 'leader_board', 'c2w_rides', 'c2w_distance',
                      '2x30', '30x40']

        if company in companies and month in months and challenge in challenges:

            consolidate_results_options = defaultdict(lambda: self.dummy_function, {
                'bosch_even': self.calculate_challenges_stats.consolidate_bosch_even_challenges_result,
                'cadence90_odd': self.calculate_challenges_stats.consolidate_odd_challenges_result,
                'tok_odd': self.tok_odd_challenges.consolidate_tok_odd_challenges_result,
                '': self.dummy_function
            })

            cache_name = "{company}_{month}_challenges_result".format(company=company, month=month)
            cache_result = self.iron_cache_resource.get_cache(cache_name, challenge)
            if cache_result:
                challenges_result = cache_result
            else:
                consolidate_results = "{company}_{month}".format(company=company, month=month)
                consolidate_results_options[consolidate_results]()
                cache_result = self.iron_cache_resource.get_cache(cache_name, challenge)
                if cache_result:
                    challenges_result = cache_result

        return challenges_result

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
            else:
                logging.warning("Athlete does not exist in the database.")


class CalculateChallengesStats:

    def __init__(self):
        self.app_constants = AppConstants()
        self.app_variables = AppVariables()
        self.operations = Operations()
        self.strava_resource = StravaResource()
        self.telegram_resource = TelegramResource()
        self.database_resource = DatabaseResource()
        self.iron_cache_resource = IronCacheResource()
        self.tok_odd_month_challenge = ToKOddMonth()

    def is_lat_long_within_range(self, lat1, long1, lat2, long2, earth_radius=6372.8):
        is_within_range = False
        rad_lat = radians(lat2 - lat1)
        rad_long = radians(long2 - long1)

        lat1 = radians(lat1)
        lat2 = radians(lat2)

        a = sin(rad_lat / 2) ** 2 + \
            cos(lat1) * cos(lat2) * \
            sin(rad_long / 2) ** 2

        c = 2 * asin(sqrt(a))
        distance_km = earth_radius * c

        if distance_km < self.app_variables.location_threshold:
            is_within_range = True

        return is_within_range

    def even_challenges(self, athlete_details):
        # ride_calendar = {
        #     1: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     2: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     3: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     4: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     5: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     6: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     7: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     8: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     9: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     10: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     11: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     12: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     13: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     14: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     15: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     16: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     17: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     18: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     19: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     20: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     21: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     22: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     23: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     24: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     25: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     26: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     27: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     28: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     29: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     30: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
        #     31: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0}
        # }
        #
        # for activity in self.strava_resource.get_strava_activities_after_date_before_date(
        #         athlete_details['athlete_token'], self.app_variables.even_challenges_from_date,
        #         self.app_variables.even_challenges_to_date):
        #     activity_month = activity.start_date_local.month
        #     activity_year = activity.start_date_local.year
        #     activity_day = activity.start_date_local.day
        #     activity_distance = self.operations.meters_to_kilometers(float(activity.distance))
        #     activity_elevation = self.operations.remove_decimal_point(float(activity.total_elevation_gain))
        #     activity_time = unithelper.timedelta_to_seconds(activity.moving_time)
        #     logging.info(
        #         "Type: %s | Month: %s | Year: %s | Day: %s | Distance: %s | Time: %s | Elevation: %s",
        #         activity.type, activity_month, activity_year, activity_day, activity_distance, activity_time,
        #         activity_elevation)
        #     if self.operations.supported_activities_for_challenges(
        #             activity) and activity_month == self.app_variables.even_challenges_month and activity_year == self.app_variables.even_challenges_year:
        #
        #         ride_calendar[activity_day]["distance"] += activity_distance
        #         ride_calendar[activity_day]["elevation"] += activity_elevation
        #         # Minimum 30 mins or 10 kms for 1 activity
        #         if activity_time >= 1800 or activity_distance >= 10.0:
        #             ride_calendar[activity_day]["activities"] += 1
        #
        #         if activity_distance >= 100.0:
        #             ride_calendar[activity_day]["bonus_distance_sot"] = 100
        #         elif activity_distance >= 50.0:
        #             ride_calendar[activity_day]["bonus_distance_sot"] = 50 if ride_calendar[activity_day][
        #                                                                           "bonus_distance_sot"] < 50 else \
        #                 ride_calendar[activity_day]["bonus_distance_sot"]
        #         elif activity_distance >= 20.0:
        #             ride_calendar[activity_day]["bonus_distance_sot"] = 20 if ride_calendar[activity_day][
        #                                                                           "bonus_distance_sot"] < 20 else \
        #                 ride_calendar[activity_day]["bonus_distance_sot"]
        #
        #         if activity_elevation >= 1000:
        #             ride_calendar[activity_day]["bonus_elevation_sot"] = 1000
        #         elif activity_elevation >= 500:
        #             ride_calendar[activity_day]["bonus_elevation_sot"] = 500 if ride_calendar[activity_day][
        #                                                                             "bonus_elevation_sot"] < 500 else \
        #                 ride_calendar[activity_day]["bonus_elevation_sot"]
        #
        # logging.info("Ride Calendar: %s", ride_calendar)
        #
        # for day in ride_calendar:
        #     # A cap of 100 kms(single ride) is set for base points.
        #     ride_calendar[day]["distance"] = ride_calendar[day]["distance"] if ride_calendar[day][
        #                                                                            "distance"] <= 100.0 else 100.0
        #     # A cap of 1500 meters(single ride) of elevation gain is set for base points.
        #     ride_calendar[day]["elevation"] = ride_calendar[day]["elevation"] if ride_calendar[day][
        #                                                                              "elevation"] <= 1500 else 1500
        #
        # logging.info("Ride Calendar: %s", ride_calendar)
        #
        # total_distance = 0.0
        # total_elevation = 0
        # total_activities = 0
        # total_hundreds = 0
        # total_fifties = 0
        # total_twenties = 0
        #
        # for day in ride_calendar:
        #     total_distance += ride_calendar[day]["distance"]
        #     total_elevation += ride_calendar[day]["elevation"]
        #     total_activities += ride_calendar[day]["activities"]
        #     if ride_calendar[day]["bonus_distance_sot"] == 100:
        #         total_hundreds += 1
        #     elif ride_calendar[day]["bonus_distance_sot"] == 50:
        #         total_fifties += 1
        #     elif ride_calendar[day]["bonus_distance_sot"] == 20:
        #         total_twenties += 1
        #
        #     if day in [1, 31]:
        #         total_distance += ride_calendar[day]["distance"]
        #         total_elevation += ride_calendar[day]["elevation"]
        #         total_activities += ride_calendar[day]["activities"]
        #
        total_points = 0
        # weekend = [6, 7, 13, 14, 20, 21, 27, 28]
        #
        # for day in ride_calendar:
        #     # 100 km in a single ride on a weekend = 20 points and on a weekday = 30 points
        #     if ride_calendar[day]["bonus_distance_sot"] >= 100.0:
        #         total_points += 20 if day in weekend else 30
        #     # 50 km in a single ride on a weekend = 10 points and on a weekday = 15 points
        #     elif ride_calendar[day]["bonus_distance_sot"] >= 50.0:
        #         total_points += 10 if day in weekend else 15
        #     # 20 km in a single ride = 5 points
        #     elif ride_calendar[day]["bonus_distance_sot"] >= 20.0:
        #         total_points += 5
        #
        #     # 1000 meters of elevation gain in a single ride = 25 points
        #     if ride_calendar[day]["bonus_elevation_sot"] >= 1000:
        #         total_points += 25
        #     # 500 meters of elevation gain in a single ride = 10 points
        #     elif ride_calendar[day]["bonus_elevation_sot"] >= 500:
        #         total_points += 10
        #
        #     if day in [1, 31]:
        #         if ride_calendar[day]["bonus_distance_sot"] >= 100.0:
        #             total_points += 20 if day in weekend else 30
        #         elif ride_calendar[day]["bonus_distance_sot"] >= 50.0:
        #             total_points += 10 if day in weekend else 15
        #         elif ride_calendar[day]["bonus_distance_sot"] >= 20.0:
        #             total_points += 5
        #         if ride_calendar[day]["bonus_elevation_sot"] >= 1000:
        #             total_points += 25
        #         elif ride_calendar[day]["bonus_elevation_sot"] >= 500:
        #             total_points += 10
        #
        # # 10 km = 1 point
        # total_points += int(total_distance / 10)
        # # 100 meters = 1 point (Elevation gain)
        # total_points += int(total_elevation / 100)
        # # 1 activity = 1 point
        # total_points += total_activities
        # # 1000 kms in a month = 150 points
        # if total_distance >= 1000.0:
        #     total_points += 150
        # # 10000 meters of elevation gain in a month = 150 points
        # if total_elevation >= 10000:
        #     total_points += 150
        #
        # # 100 km rides for 10 days in a month = 200
        # if total_hundreds >= 10:
        #     total_points += 200
        # # 50 km rides for 10 days in a month = 100 points**
        # if total_fifties >= 10:
        #     total_points += 100
        # # 20 km on all days of the month = 250 points
        # if total_twenties == 31:
        #     total_points += 250
        # # 20 km for 20 days in a month = 150 points
        # elif total_twenties >= 20:
        #     total_points += 150
        #
        # # 20 km for 5 successive days = 75 points
        # # 50 km for 5 successive days = 100 points*
        # # 100 km for 3 successive days = 100 points
        # hundreds_streak = 0
        # fifties_streak = 0
        # twenties_streak = 0
        # for day in ride_calendar:
        #     distance = ride_calendar[day]["bonus_distance_sot"]
        #     if distance == 100:
        #         hundreds_streak += 1
        #         fifties_streak += 1
        #         twenties_streak += 1
        #     else:
        #         hundreds_streak = 0
        #         if distance == 50:
        #             fifties_streak += 1
        #             twenties_streak += 1
        #         else:
        #             fifties_streak = 0
        #             if distance == 20:
        #                 twenties_streak += 1
        #             else:
        #                 twenties_streak = 0
        #     if hundreds_streak == 3:
        #         total_points += 100
        #         hundreds_streak = 0
        #         fifties_streak = 0
        #         twenties_streak = 0
        #     elif fifties_streak == 5:
        #         total_points += 100
        #         hundreds_streak = 0
        #         fifties_streak = 0
        #         twenties_streak = 0
        #     elif twenties_streak == 5:
        #         total_points += 100
        #         hundreds_streak = 0
        #         fifties_streak = 0
        #         twenties_streak = 0
        #
        # logging.info("total_distance: %s | total_elevation: %s, total_activities: %s | total_points: %s | "
        #              "total_hundreds: %s | total_fifties: %s | total_twenties: %s | ride_calendar: %s | "
        #              "hundreds_streak: %s | fifties_streak: %s | twenties_streak: %s",
        #              total_distance, total_elevation, total_activities, total_points, total_hundreds, total_fifties,
        #              total_twenties, ride_calendar, hundreds_streak, fifties_streak, twenties_streak)

        if self.database_resource.write_operation(self.app_constants.QUERY_UPDATE_EVEN_CHALLENGES_DATA.format(
                challenges_data=ujson.dumps({'athlete_id': athlete_details['athlete_id'], 'points': total_points}),
                athlete_id=athlete_details['athlete_id'])):
            self.telegram_resource.send_message(
                "Updated Cadence90 even challenges data for {name}.".format(name=athlete_details['name']))
        else:
            self.telegram_resource.send_message(
                "Failed to update Cadence90 even challenges data for {name}".format(name=athlete_details['name']))

    def odd_challenges(self, athlete_details):
        ride_calendar = {
            1: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            2: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            3: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            4: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            5: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            6: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            7: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            8: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            9: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            10: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            11: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            12: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            13: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            14: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            15: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            16: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            17: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            18: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            19: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            20: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            21: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            22: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            23: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            24: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            25: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            26: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            27: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            28: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            29: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            30: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0},
            31: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0, "bonus_elevation_sot": 0}
        }

        for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                athlete_details['athlete_token'], self.app_variables.odd_challenges_from_date,
                self.app_variables.odd_challenges_to_date):
            activity_month = activity.start_date_local.month
            activity_year = activity.start_date_local.year
            activity_day = activity.start_date_local.day
            activity_distance = self.operations.meters_to_kilometers(float(activity.distance))
            activity_elevation = self.operations.remove_decimal_point(float(activity.total_elevation_gain))
            activity_time = unithelper.timedelta_to_seconds(activity.moving_time)
            logging.info(
                "Type: %s | Month: %s | Year: %s | Day: %s | Distance: %s | Time: %s | Elevation: %s",
                activity.type, activity_month, activity_year, activity_day, activity_distance, activity_time,
                activity_elevation)
            if self.operations.supported_activities_for_challenges(
                    activity) and activity_month == self.app_variables.odd_challenges_month and activity_year == self.app_variables.odd_challenges_year:

                ride_calendar[activity_day]["distance"] += activity_distance
                ride_calendar[activity_day]["elevation"] += activity_elevation
                # Minimum 30 mins or 10 kms for 1 activity
                if activity_time >= 1800 or activity_distance >= 10.0:
                    ride_calendar[activity_day]["activities"] += 1

                if activity_distance >= 100.0:
                    ride_calendar[activity_day]["bonus_distance_sot"] = 100
                elif activity_distance >= 50.0:
                    ride_calendar[activity_day]["bonus_distance_sot"] = 50 if ride_calendar[activity_day][
                                                                                  "bonus_distance_sot"] < 50 else \
                    ride_calendar[activity_day]["bonus_distance_sot"]
                elif activity_distance >= 20.0:
                    ride_calendar[activity_day]["bonus_distance_sot"] = 20 if ride_calendar[activity_day][
                                                                                  "bonus_distance_sot"] < 20 else \
                    ride_calendar[activity_day]["bonus_distance_sot"]

                if activity_elevation >= 1000:
                    ride_calendar[activity_day]["bonus_elevation_sot"] = 1000
                elif activity_elevation >= 500:
                    ride_calendar[activity_day]["bonus_elevation_sot"] = 500 if ride_calendar[activity_day][
                                                                                    "bonus_elevation_sot"] < 500 else \
                    ride_calendar[activity_day]["bonus_elevation_sot"]

        logging.info("Ride Calendar: %s", ride_calendar)

        for day in ride_calendar:
            # A cap of 100 kms(single ride) is set for base points.
            ride_calendar[day]["distance"] = ride_calendar[day]["distance"] if ride_calendar[day][
                                                                                   "distance"] <= 100.0 else 100.0
            # A cap of 1500 meters(single ride) of elevation gain is set for base points.
            ride_calendar[day]["elevation"] = ride_calendar[day]["elevation"] if ride_calendar[day][
                                                                                     "elevation"] <= 1500 else 1500

        logging.info("Ride Calendar: %s", ride_calendar)

        total_distance = 0.0
        total_elevation = 0
        total_activities = 0
        total_hundreds = 0
        total_fifties = 0
        total_twenties = 0

        for day in ride_calendar:
            total_distance += ride_calendar[day]["distance"]
            total_elevation += ride_calendar[day]["elevation"]
            total_activities += ride_calendar[day]["activities"]
            if ride_calendar[day]["bonus_distance_sot"] == 100:
                total_hundreds += 1
            elif ride_calendar[day]["bonus_distance_sot"] == 50:
                total_fifties += 1
            elif ride_calendar[day]["bonus_distance_sot"] == 20:
                total_twenties += 1

            if day in [1, 31]:
                total_distance += ride_calendar[day]["distance"]
                total_elevation += ride_calendar[day]["elevation"]
                total_activities += ride_calendar[day]["activities"]

        total_points = 0
        weekend = [6, 7, 13, 14, 20, 21, 27, 28]

        for day in ride_calendar:
            # 100 km in a single ride on a weekend = 20 points and on a weekday = 30 points
            if ride_calendar[day]["bonus_distance_sot"] >= 100.0:
                total_points += 20 if day in weekend else 30
            # 50 km in a single ride on a weekend = 10 points and on a weekday = 15 points
            elif ride_calendar[day]["bonus_distance_sot"] >= 50.0:
                total_points += 10 if day in weekend else 15
            # 20 km in a single ride = 5 points
            elif ride_calendar[day]["bonus_distance_sot"] >= 20.0:
                total_points += 5

            # 1000 meters of elevation gain in a single ride = 25 points
            if ride_calendar[day]["bonus_elevation_sot"] >= 1000:
                total_points += 25
            # 500 meters of elevation gain in a single ride = 10 points
            elif ride_calendar[day]["bonus_elevation_sot"] >= 500:
                total_points += 10

            if day in [1, 31]:
                if ride_calendar[day]["bonus_distance_sot"] >= 100.0:
                    total_points += 20 if day in weekend else 30
                elif ride_calendar[day]["bonus_distance_sot"] >= 50.0:
                    total_points += 10 if day in weekend else 15
                elif ride_calendar[day]["bonus_distance_sot"] >= 20.0:
                    total_points += 5
                if ride_calendar[day]["bonus_elevation_sot"] >= 1000:
                    total_points += 25
                elif ride_calendar[day]["bonus_elevation_sot"] >= 500:
                    total_points += 10

        # 10 km = 1 point
        total_points += int(total_distance / 10)
        # 100 meters = 1 point (Elevation gain)
        total_points += int(total_elevation / 100)
        # 1 activity = 1 point
        total_points += total_activities
        # 1000 kms in a month = 150 points
        if total_distance >= 1000.0:
            total_points += 150
        # 10000 meters of elevation gain in a month = 150 points
        if total_elevation >= 10000:
            total_points += 150

        # 100 km rides for 10 days in a month = 200
        if total_hundreds >= 10:
            total_points += 200
        # 50 km rides for 10 days in a month = 100 points**
        if total_fifties >= 10:
            total_points += 100
        # 20 km on all days of the month = 250 points
        if total_twenties == 31:
            total_points += 250
        # 20 km for 20 days in a month = 150 points
        elif total_twenties >= 20:
            total_points += 150

        # 20 km for 5 successive days = 75 points
        # 50 km for 5 successive days = 100 points*
        # 100 km for 3 successive days = 100 points
        hundreds_streak = 0
        fifties_streak = 0
        twenties_streak = 0
        for day in ride_calendar:
            distance = ride_calendar[day]["bonus_distance_sot"]
            if distance == 100:
                hundreds_streak += 1
                fifties_streak += 1
                twenties_streak += 1
            else:
                hundreds_streak = 0
                if distance == 50:
                    fifties_streak += 1
                    twenties_streak += 1
                else:
                    fifties_streak = 0
                    if distance == 20:
                        twenties_streak += 1
                    else:
                        twenties_streak = 0
            if hundreds_streak == 3:
                total_points += 100
                hundreds_streak = 0
                fifties_streak = 0
                twenties_streak = 0
            elif fifties_streak == 5:
                total_points += 100
                hundreds_streak = 0
                fifties_streak = 0
                twenties_streak = 0
            elif twenties_streak == 5:
                total_points += 100
                hundreds_streak = 0
                fifties_streak = 0
                twenties_streak = 0

        logging.info("total_distance: %s | total_elevation: %s, total_activities: %s | total_points: %s | "
                     "total_hundreds: %s | total_fifties: %s | total_twenties: %s | ride_calendar: %s | "
                     "hundreds_streak: %s | fifties_streak: %s | twenties_streak: %s",
                     total_distance, total_elevation, total_activities, total_points, total_hundreds, total_fifties,
                     total_twenties, ride_calendar, hundreds_streak, fifties_streak, twenties_streak)

        if self.database_resource.write_operation(self.app_constants.QUERY_UPDATE_ODD_CHALLENGES_DATA.format(
                challenges_data=ujson.dumps({'athlete_id': athlete_details['athlete_id'], 'points': total_points}),
                athlete_id=athlete_details['athlete_id'])):
            self.telegram_resource.send_message(
                "Updated Cadence90 odd challenges data for {name}.".format(name=athlete_details['name']))
        else:
            self.telegram_resource.send_message(
                "Failed to update Cadence90 odd challenges data for {name}".format(name=athlete_details['name']))

    def is_c2w_eligible(self, start_gps, end_gps):
        lat_long = self.app_variables.location_gps
        is_eligible_to = False
        is_eligible_from = False
        for location in lat_long:
            work_lat = lat_long[location][0]
            work_long = lat_long[location][1]
            if self.is_lat_long_within_range(work_lat, work_long, end_gps[0], end_gps[1]):
                is_eligible_to = True
            if self.is_lat_long_within_range(work_lat, work_long, start_gps[0], start_gps[1]):
                is_eligible_from = True

        return is_eligible_to, is_eligible_from

    def bosch_even_challenges(self, athlete_details):
        cycle_to_work_rides_calendar = {
            1: {'to': False, 'from': False}, 2: {'to': False, 'from': False}, 3: {'to': False, 'from': False},
            4: {'to': False, 'from': False}, 5: {'to': False, 'from': False}, 6: {'to': False, 'from': False},
            7: {'to': False, 'from': False}, 8: {'to': False, 'from': False}, 9: {'to': False, 'from': False},
            10: {'to': False, 'from': False}, 11: {'to': False, 'from': False}, 12: {'to': False, 'from': False},
            13: {'to': False, 'from': False}, 14: {'to': False, 'from': False}, 15: {'to': False, 'from': False},
            16: {'to': False, 'from': False}, 17: {'to': False, 'from': False}, 18: {'to': False, 'from': False},
            19: {'to': False, 'from': False}, 20: {'to': False, 'from': False}, 21: {'to': False, 'from': False},
            22: {'to': False, 'from': False}, 23: {'to': False, 'from': False}, 24: {'to': False, 'from': False},
            25: {'to': False, 'from': False}, 26: {'to': False, 'from': False}, 27: {'to': False, 'from': False},
            28: {'to': False, 'from': False}, 29: {'to': False, 'from': False}, 30: {'to': False, 'from': False},
            31: {'to': False, 'from': False}
        }
        cycle_to_work_rides_count = 0
        cycle_to_work_rides_points = 0

        cycle_to_work_distance_calendar = {
            1: {'to': 0.0, 'from': 0.0}, 2: {'to': 0.0, 'from': 0.0}, 3: {'to': 0.0, 'from': 0.0},
            4: {'to': 0.0, 'from': 0.0}, 5: {'to': 0.0, 'from': 0.0}, 6: {'to': 0.0, 'from': 0.0},
            7: {'to': 0.0, 'from': 0.0}, 8: {'to': 0.0, 'from': 0.0}, 9: {'to': 0.0, 'from': 0.0},
            10: {'to': 0.0, 'from': 0.0}, 11: {'to': 0.0, 'from': 0.0}, 12: {'to': 0.0, 'from': 0.0},
            13: {'to': 0.0, 'from': 0.0}, 14: {'to': 0.0, 'from': 0.0}, 15: {'to': 0.0, 'from': 0.0},
            16: {'to': 0.0, 'from': 0.0}, 17: {'to': 0.0, 'from': 0.0}, 18: {'to': 0.0, 'from': 0.0},
            19: {'to': 0.0, 'from': 0.0}, 20: {'to': 0.0, 'from': 0.0}, 21: {'to': 0.0, 'from': 0.0},
            22: {'to': 0.0, 'from': 0.0}, 23: {'to': 0.0, 'from': 0.0}, 24: {'to': 0.0, 'from': 0.0},
            25: {'to': 0.0, 'from': 0.0}, 26: {'to': 0.0, 'from': 0.0}, 27: {'to': 0.0, 'from': 0.0},
            28: {'to': 0.0, 'from': 0.0}, 29: {'to': 0.0, 'from': 0.0}, 30: {'to': 0.0, 'from': 0.0},
            31: {'to': 0.0, 'from': 0.0}
        }
        cycle_to_work_distance_count = 0
        cycle_to_work_distance_points = 0

        two_km_rides = 0
        two_km_points = 0

        forty_min_rides = 0
        forty_min_points = 0
        is_eligible_for_forty_mins_rides_bonus = False

        total_distance = 0.0
        is_eligible_for_distance_bonus = False

        try:
            for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                    athlete_details['athlete_token'], self.app_variables.even_challenges_from_date,
                    self.app_variables.even_challenges_to_date):
                activity_month = activity.start_date_local.month
                activity_year = activity.start_date_local.year
                activity_day = activity.start_date_local.day
                activity_distance = float(activity.distance)
                activity_time = unithelper.timedelta_to_seconds(activity.moving_time)
                try:
                    start_gps = [activity.start_latlng.lat, activity.start_latlng.lon]
                    end_gps = [activity.end_latlng.lat, activity.end_latlng.lon]
                except AttributeError:
                    start_gps = None
                    end_gps = None

                logging.info(
                    "Type: %s | Month: %s | Year: %s | Day: %s | Distance: %s | Time: %s | Start GPS: %s | End GPS: %s",
                    activity.type, activity_month, activity_year, activity_day, activity_distance, activity_time,
                    start_gps,
                    end_gps)
                if self.operations.supported_activities_for_challenges(activity) and not self.operations.is_indoor(
                        activity) and activity_month == self.app_variables.even_challenges_month and activity_year == self.app_variables.even_challenges_year:
                    if start_gps and end_gps:
                        is_eligible_to, is_eligible_from = self.is_c2w_eligible(start_gps, end_gps)
                        if is_eligible_to:
                            cycle_to_work_rides_calendar[activity_day]['to'] = True
                            cycle_to_work_rides_count += 1
                            cycle_to_work_rides_points += 20
                            cycle_to_work_distance_calendar[activity_day]['to'] = activity_distance / 1000.0
                            cycle_to_work_distance_count += activity_distance / 1000.0
                            cycle_to_work_distance_points += int(activity_distance / 1000)
                        if is_eligible_from:
                            cycle_to_work_rides_calendar[activity_day]['from'] = True
                            cycle_to_work_rides_count += 1
                            cycle_to_work_rides_points += 20
                            cycle_to_work_distance_calendar[activity_day]['from'] = activity_distance / 1000.0
                            cycle_to_work_distance_count += activity_distance / 1000.0
                            cycle_to_work_distance_points += int(activity_distance / 1000)
                    if activity_distance >= 2000.0:
                        two_km_rides += 1
                        two_km_points += 15
                    if activity_time >= 2400:
                        forty_min_rides += 1
                        forty_min_points += 20
                        if activity_distance >= 50000:
                            is_eligible_for_forty_mins_rides_bonus = True
                    total_distance += activity_distance
                    if activity_distance >= 150000.0:
                        is_eligible_for_distance_bonus = True
        except Exception:
            logging.error(traceback.format_exc())
            self.telegram_resource.send_message(
                "Could not get stats for {}.\nException: {}".format(athlete_details["athlete_id"],
                                                                    traceback.format_exc()))
            pass

        logging.info(
            "Total distance: %s | 2 km rides : %s | 40 min rides: %s | Cycle to Work Calendar: %s Cycle to Work Distance Calendar: %s",
            total_distance, two_km_rides, forty_min_rides, cycle_to_work_rides_calendar,
            cycle_to_work_distance_calendar)

        challenges = athlete_details['bosch_even_challenges']

        challenges_stats = {
            'c2w_days': 0,
            'c2w_rides': 0,
            'c2w_rides_points': 0,
            'c2w_distance_days': 0,
            'c2w_distance': 0,
            'c2w_distance_points': 0,
            '2x30': 0,
            '2x30_points': 0,
            '40x30': 0,
            '40x30_points': 0,
            'distance': 0.0,
            'distance_points': 0,
            'athlete_id': athlete_details['athlete_id'],
            'location': challenges['location']
        }

        if "c2w_rides" in challenges['id']:
            for day in cycle_to_work_rides_calendar:
                if cycle_to_work_rides_calendar[day]['to'] and cycle_to_work_rides_calendar[day]['from']:
                    challenges_stats['c2w_days'] += 1

            challenges_stats['c2w_rides'] += cycle_to_work_rides_count
            challenges_stats['c2w_rides_points'] += cycle_to_work_rides_points
            challenges_stats[
                'c2w_rides_points'] = 500 if cycle_to_work_rides_points > 500 else cycle_to_work_rides_points
            if cycle_to_work_rides_count >= 1:
                challenges_stats['c2w_rides_points'] += 50
            if cycle_to_work_rides_count >= 2:
                challenges_stats['c2w_rides_points'] += 50
            if challenges_stats['c2w_days'] >= 15:
                challenges_stats['c2w_rides_points'] += 100

        elif "c2w_distance" in challenges['id']:
            for day in cycle_to_work_distance_calendar:
                if cycle_to_work_distance_calendar[day]['to'] > 0.0 and cycle_to_work_distance_calendar[day][
                    'from'] > 0.0:
                    challenges_stats['c2w_distance_days'] += 1

            challenges_stats['c2w_distance'] += cycle_to_work_distance_count
            challenges_stats['c2w_distance_points'] += cycle_to_work_distance_points
            challenges_stats[
                'c2w_distance_points'] = 500 if cycle_to_work_distance_points > 500 else cycle_to_work_distance_points
            if cycle_to_work_rides_count >= 1:
                challenges_stats['c2w_distance_points'] += 50
            if cycle_to_work_rides_count >= 2:
                challenges_stats['c2w_distance_points'] += 50
            if challenges_stats['c2w_distance_points'] >= 550:
                challenges_stats['c2w_distance_points'] += 100

        if "2x30" in challenges['id']:
            challenges_stats['2x30'] += two_km_rides
            challenges_stats['2x30_points'] = two_km_points
            challenges_stats['2x30_points'] = 450 if two_km_points > 450 else two_km_points
            if cycle_to_work_rides_count >= 1:
                challenges_stats['2x30_points'] += 50
            if cycle_to_work_rides_count >= 2:
                challenges_stats['2x30_points'] += 50
            if two_km_rides >= 30:
                challenges_stats['2x30_points'] += 50
            if two_km_rides >= 35:
                challenges_stats['2x30_points'] += 50

        elif "40x30" in challenges['id']:
            challenges_stats['40x30'] += forty_min_rides
            challenges_stats['40x30_points'] = forty_min_points
            challenges_stats['40x30_points'] = 600 if forty_min_points > 600 else forty_min_points
            if forty_min_rides >= 30:
                challenges_stats['40x30_points'] += 20
                if is_eligible_for_forty_mins_rides_bonus:
                    challenges_stats['40x30_points'] += 50

        elif "distance" in challenges['id']:
            challenges_stats['distance'] += total_distance
            distance_points = int(total_distance / 1000)
            challenges_stats['distance_points'] = 600 if distance_points > 600 else distance_points
            if total_distance >= 1000000.0:
                challenges_stats['distance_points'] += 50
                if is_eligible_for_distance_bonus:
                    challenges_stats['distance_points'] += 50

        if self.database_resource.write_operation(self.app_constants.QUERY_UPDATE_BOSCH_EVEN_CHALLENGES_DATA.format(
                bosch_even_challenges_data=ujson.dumps(challenges_stats), athlete_id=athlete_details['athlete_id'])):
            self.telegram_resource.send_message(
                "Updated Bosch even challenges data for {name}.".format(name=athlete_details['name']))
        else:
            self.telegram_resource.send_message(
                "Failed to update Bosch even challenges data for {name}".format(name=athlete_details['name']))

    def consolidate_bosch_even_challenges_result(self):
        cycle_to_work_rides = list()
        cycle_to_work_distance = list()
        two_km_rides = list()
        forty_mins_rides = list()
        distance = list()
        leader_board = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_BOSCH_EVEN_CHALLENGES_DATA)
        for result in results:
            name = result[0]
            challenges = result[1]
            challenges_data = result[2]

            if challenges:
                leader_board.append({"athlete_id": challenges_data['athlete_id'], "name": name,
                                     "location": challenges_data['location'],
                                     "points": challenges_data['c2w_rides_points'] + challenges_data[
                                         'c2w_distance_points'] + challenges_data['2x30_points'] + challenges_data[
                                                   '40x30_points'] + challenges_data['distance_points']})
                if "c2w_rides" in challenges['id']:
                    cycle_to_work_rides.append(
                        {'name': name, 'value': challenges_data['c2w_days'],
                         'points': challenges_data['c2w_rides_points'],
                         'rides': challenges_data['c2w_rides'], 'athlete_id': challenges_data['athlete_id'],
                         'location': challenges_data['location']})
                elif "c2w_distance" in challenges['id']:
                    cycle_to_work_distance.append(
                        {'name': name, 'value': challenges_data['c2w_distance_days'],
                         'points': challenges_data['c2w_distance_points'],
                         'rides': challenges_data['c2w_distance'], 'athlete_id': challenges_data['athlete_id'],
                         'location': challenges_data['location']})
                if "2x30" in challenges['id']:
                    two_km_rides.append(
                        {'name': name, 'value': challenges_data['2x30'], 'points': challenges_data['2x30_points'],
                         'athlete_id': challenges_data['athlete_id'], 'location': challenges_data['location']})
                elif "40x30" in challenges['id']:
                    forty_mins_rides.append(
                        {'name': name, 'value': challenges_data['40x30'], 'points': challenges_data['40x30_points'],
                         'athlete_id': challenges_data['athlete_id'], 'location': challenges_data['location']})
                elif "distance" in challenges['id']:
                    distance.append(
                        {'name': name, 'value': self.operations.meters_to_kilometers(challenges_data['distance']),
                         'points': challenges_data['distance_points'], 'athlete_id': challenges_data['athlete_id'],
                         'location': challenges_data['location']})

        c2w_rides_points_temp = sorted(cycle_to_work_rides, key=operator.itemgetter('points', 'value'), reverse=True)
        c2w_rides_distance_temp = sorted(cycle_to_work_distance, key=operator.itemgetter('points', 'value'),
                                         reverse=True)
        two_km_temp = sorted(two_km_rides, key=operator.itemgetter('points', 'value'), reverse=True)
        forty_mins_temp = sorted(forty_mins_rides, key=operator.itemgetter('points', 'value'), reverse=True)
        distance_temp = sorted(distance, key=operator.itemgetter('points', 'value'), reverse=True)
        leader_board_temp = sorted(leader_board, key=operator.itemgetter('points'), reverse=True)

        c2w_rides_points_sorted = list()
        rank = 1
        for athlete in c2w_rides_points_temp:
            c2w_rides_points_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'rides': athlete['rides'], 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        c2w_distance_points_sorted = list()
        rank = 1
        for athlete in c2w_rides_distance_temp:
            c2w_distance_points_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'rides': athlete['rides'], 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        two_km_rides_sorted = list()
        rank = 1
        for athlete in two_km_temp:
            two_km_rides_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        forty_mins_rides_sorted = list()
        rank = 1
        for athlete in forty_mins_temp:
            forty_mins_rides_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        distance_sorted = list()
        rank = 1
        for athlete in distance_temp:
            distance_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'distance': athlete['value'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        leader_board_sorted = list()
        rank = 1
        for athlete in leader_board_temp:
            leader_board_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "c2w_rides",
                                           ujson.dumps(c2w_rides_points_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "c2w_distance",
                                           ujson.dumps(c2w_distance_points_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "2x30",
                                           ujson.dumps(two_km_rides_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "30x40",
                                           ujson.dumps(forty_mins_rides_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "distance",
                                           ujson.dumps(distance_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "leader_board",
                                           ujson.dumps(leader_board_sorted))

    def consolidate_even_challenges_result(self):
        even_challenge = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_EVEN_CHALLENGES_DATA)
        for result in results:
            name = result[0]
            challenges = result[1]
            challenges_data = result[2]

            if challenges and challenges['payment']:
                even_challenge.append({'name': name, 'value': challenges_data['points']})

        even_challenge_temp = sorted(even_challenge, key=operator.itemgetter('value'), reverse=True)

        even_challenge_sorted = list()
        rank = 1
        for athlete in even_challenge_temp:
            even_challenge_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        if len(even_challenge_sorted) == 0:
            even_challenge_sorted.append({'rank': '', 'name': '', 'value': ''})

        self.iron_cache_resource.put_cache("cadence90_even_challenges_result", "leaderboard",
                                           ujson.dumps(even_challenge_sorted))
        self.telegram_resource.send_message("Updated cache for Cadence90 even month challenges.")

    def consolidate_odd_challenges_result(self):
        odd_challenge = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_ODD_CHALLENGES_DATA)
        for result in results:
            name = result[0]
            challenges = result[1]
            challenges_data = result[2]

            if challenges and challenges['payment']:
                odd_challenge.append({'name': name, 'value': challenges_data['points']})

        odd_challenge_temp = sorted(odd_challenge, key=operator.itemgetter('value'), reverse=True)

        odd_challenge_sorted = list()
        rank = 1
        for athlete in odd_challenge_temp:
            odd_challenge_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        if len(odd_challenge_sorted) == 0:
            odd_challenge_sorted.append({'rank': '', 'name': '', 'value': ''})

        self.iron_cache_resource.put_cache("cadence90_odd_challenges_result", "leaderboard",
                                           ujson.dumps(odd_challenge_sorted))
        self.telegram_resource.send_message("Updated cache for Cadence90 odd month challenges.")

    def bosch_odd_challenges(self, athlete_details):
        cycle_to_work_rides_calendar = {
            1: {'to': False, 'from': False}, 2: {'to': False, 'from': False}, 3: {'to': False, 'from': False},
            4: {'to': False, 'from': False}, 5: {'to': False, 'from': False}, 6: {'to': False, 'from': False},
            7: {'to': False, 'from': False}, 8: {'to': False, 'from': False}, 9: {'to': False, 'from': False},
            10: {'to': False, 'from': False}, 11: {'to': False, 'from': False}, 12: {'to': False, 'from': False},
            13: {'to': False, 'from': False}, 14: {'to': False, 'from': False}, 15: {'to': False, 'from': False},
            16: {'to': False, 'from': False}, 17: {'to': False, 'from': False}, 18: {'to': False, 'from': False},
            19: {'to': False, 'from': False}, 20: {'to': False, 'from': False}, 21: {'to': False, 'from': False},
            22: {'to': False, 'from': False}, 23: {'to': False, 'from': False}, 24: {'to': False, 'from': False},
            25: {'to': False, 'from': False}, 26: {'to': False, 'from': False}, 27: {'to': False, 'from': False},
            28: {'to': False, 'from': False}, 29: {'to': False, 'from': False}, 30: {'to': False, 'from': False},
            31: {'to': False, 'from': False}
        }
        cycle_to_work_rides_count = 0
        cycle_to_work_rides_points = 0

        cycle_to_work_distance_calendar = {
            1: {'to': 0.0, 'from': 0.0}, 2: {'to': 0.0, 'from': 0.0}, 3: {'to': 0.0, 'from': 0.0},
            4: {'to': 0.0, 'from': 0.0}, 5: {'to': 0.0, 'from': 0.0}, 6: {'to': 0.0, 'from': 0.0},
            7: {'to': 0.0, 'from': 0.0}, 8: {'to': 0.0, 'from': 0.0}, 9: {'to': 0.0, 'from': 0.0},
            10: {'to': 0.0, 'from': 0.0}, 11: {'to': 0.0, 'from': 0.0}, 12: {'to': 0.0, 'from': 0.0},
            13: {'to': 0.0, 'from': 0.0}, 14: {'to': 0.0, 'from': 0.0}, 15: {'to': 0.0, 'from': 0.0},
            16: {'to': 0.0, 'from': 0.0}, 17: {'to': 0.0, 'from': 0.0}, 18: {'to': 0.0, 'from': 0.0},
            19: {'to': 0.0, 'from': 0.0}, 20: {'to': 0.0, 'from': 0.0}, 21: {'to': 0.0, 'from': 0.0},
            22: {'to': 0.0, 'from': 0.0}, 23: {'to': 0.0, 'from': 0.0}, 24: {'to': 0.0, 'from': 0.0},
            25: {'to': 0.0, 'from': 0.0}, 26: {'to': 0.0, 'from': 0.0}, 27: {'to': 0.0, 'from': 0.0},
            28: {'to': 0.0, 'from': 0.0}, 29: {'to': 0.0, 'from': 0.0}, 30: {'to': 0.0, 'from': 0.0},
            31: {'to': 0.0, 'from': 0.0}
        }
        cycle_to_work_distance_count = 0
        cycle_to_work_distance_points = 0

        two_km_rides = 0
        two_km_points = 0

        forty_min_rides = 0
        forty_min_points = 0
        is_eligible_for_forty_mins_rides_bonus = False

        total_distance = 0.0
        is_eligible_for_distance_bonus = False

        for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                athlete_details['athlete_token'], self.app_variables.odd_challenges_from_date,
                self.app_variables.odd_challenges_to_date):
            activity_month = activity.start_date_local.month
            activity_year = activity.start_date_local.year
            activity_day = activity.start_date_local.day
            activity_distance = float(activity.distance)
            activity_time = unithelper.timedelta_to_seconds(activity.moving_time)
            try:
                start_gps = [activity.start_latlng.lat, activity.start_latlng.lon]
                end_gps = [activity.end_latlng.lat, activity.end_latlng.lon]
            except AttributeError:
                start_gps = None
                end_gps = None

            logging.info(
                "Type: %s | Month: %s | Year: %s | Day: %s | Distance: %s | Time: %s | Start GPS: %s | End GPS: %s",
                activity.type, activity_month, activity_year, activity_day, activity_distance, activity_time, start_gps,
                end_gps)
            if self.operations.supported_activities_for_challenges(activity) and not self.operations.is_indoor(
                    activity) and activity_month == self.app_variables.odd_challenges_month and activity_year == self.app_variables.odd_challenges_year:
                if start_gps and end_gps:
                    is_eligible_to, is_eligible_from = self.is_c2w_eligible(start_gps, end_gps)
                    if is_eligible_to:
                        cycle_to_work_rides_calendar[activity_day]['to'] = True
                        cycle_to_work_rides_count += 1
                        cycle_to_work_rides_points += 20
                        cycle_to_work_distance_calendar[activity_day]['to'] = activity_distance / 1000.0
                        cycle_to_work_distance_count += activity_distance / 1000.0
                        cycle_to_work_distance_points += int(activity_distance / 1000)
                    if is_eligible_from:
                        cycle_to_work_rides_calendar[activity_day]['from'] = True
                        cycle_to_work_rides_count += 1
                        cycle_to_work_rides_points += 20
                        cycle_to_work_distance_calendar[activity_day]['from'] = activity_distance / 1000.0
                        cycle_to_work_distance_count += activity_distance / 1000.0
                        cycle_to_work_distance_points += int(activity_distance / 1000)
                if activity_distance >= 2000.0:
                    two_km_rides += 1
                    two_km_points += 15
                if activity_time >= 2400:
                    forty_min_rides += 1
                    forty_min_points += 20
                    if activity_distance >= 50000:
                        is_eligible_for_forty_mins_rides_bonus = True
                total_distance += activity_distance
                if activity_distance >= 150000.0:
                    is_eligible_for_distance_bonus = True

        logging.info(
            "Total distance: %s | 2 km rides : %s | 40 min rides: %s | Cycle to Work Calendar: %s Cycle to Work Distance Calendar: %s",
            total_distance, two_km_rides, forty_min_rides, cycle_to_work_rides_calendar,
            cycle_to_work_distance_calendar)

        challenges = athlete_details['bosch_odd_challenges']

        challenges_stats = {
            'c2w_days': 0,
            'c2w_rides': 0,
            'c2w_rides_points': 0,
            'c2w_distance_days': 0,
            'c2w_distance': 0,
            'c2w_distance_points': 0,
            '2x30': 0,
            '2x30_points': 0,
            '40x30': 0,
            '40x30_points': 0,
            'distance': 0.0,
            'distance_points': 0,
            'athlete_id': athlete_details['athlete_id'],
            'location': challenges['location']
        }

        if "c2w_rides" in challenges['id']:
            for day in cycle_to_work_rides_calendar:
                if cycle_to_work_rides_calendar[day]['to'] and cycle_to_work_rides_calendar[day]['from']:
                    challenges_stats['c2w_days'] += 1

            challenges_stats['c2w_rides'] += cycle_to_work_rides_count
            challenges_stats['c2w_rides_points'] += cycle_to_work_rides_points
            challenges_stats[
                'c2w_rides_points'] = 500 if cycle_to_work_rides_points > 500 else cycle_to_work_rides_points
            if cycle_to_work_rides_count >= 1:
                challenges_stats['c2w_rides_points'] += 50
            if cycle_to_work_rides_count >= 2:
                challenges_stats['c2w_rides_points'] += 50
            if challenges_stats['c2w_days'] >= 15:
                challenges_stats['c2w_rides_points'] += 100

        elif "c2w_distance" in challenges['id']:
            for day in cycle_to_work_distance_calendar:
                if cycle_to_work_distance_calendar[day]['to'] > 0.0 and cycle_to_work_distance_calendar[day][
                    'from'] > 0.0:
                    challenges_stats['c2w_distance_days'] += 1

            challenges_stats['c2w_distance'] += cycle_to_work_distance_count
            challenges_stats['c2w_distance_points'] += cycle_to_work_distance_points
            challenges_stats[
                'c2w_distance_points'] = 500 if cycle_to_work_distance_points > 500 else cycle_to_work_distance_points
            if cycle_to_work_rides_count >= 1:
                challenges_stats['c2w_distance_points'] += 50
            if cycle_to_work_rides_count >= 2:
                challenges_stats['c2w_distance_points'] += 50
            if challenges_stats['c2w_distance_points'] >= 550:
                challenges_stats['c2w_distance_points'] += 100

        if "2x30" in challenges['id']:
            challenges_stats['2x30'] += two_km_rides
            challenges_stats['2x30_points'] = two_km_points
            challenges_stats['2x30_points'] = 450 if two_km_points > 450 else two_km_points
            if cycle_to_work_rides_count >= 1:
                challenges_stats['2x30_points'] += 50
            if cycle_to_work_rides_count >= 2:
                challenges_stats['2x30_points'] += 50
            if two_km_rides >= 30:
                challenges_stats['2x30_points'] += 50
            if two_km_rides >= 35:
                challenges_stats['2x30_points'] += 50

        elif "40x30" in challenges['id']:
            challenges_stats['40x30'] += forty_min_rides
            challenges_stats['40x30_points'] = forty_min_points
            challenges_stats['40x30_points'] = 600 if forty_min_points > 600 else forty_min_points
            if forty_min_rides >= 30:
                challenges_stats['40x30_points'] += 20
                if is_eligible_for_forty_mins_rides_bonus:
                    challenges_stats['40x30_points'] += 50

        elif "distance" in challenges['id']:
            challenges_stats['distance'] += total_distance
            distance_points = int(total_distance / 1000)
            challenges_stats['distance_points'] = 600 if distance_points > 600 else distance_points
            if total_distance >= 1000000.0:
                challenges_stats['distance_points'] += 50
                if is_eligible_for_distance_bonus:
                    challenges_stats['distance_points'] += 50

        if self.database_resource.write_operation(self.app_constants.QUERY_UPDATE_BOSCH_ODD_CHALLENGES_DATA.format(
                bosch_odd_challenges_data=ujson.dumps(challenges_stats), athlete_id=athlete_details['athlete_id'])):
            self.telegram_resource.send_message(
                "Updated Bosch odd challenges data for {name}.".format(name=athlete_details['name']))
        else:
            self.telegram_resource.send_message(
                "Failed to update Bosch odd challenges data for {name}".format(name=athlete_details['name']))

    def consolidate_bosch_odd_challenges_result(self):
        cycle_to_work_rides = list()
        cycle_to_work_distance = list()
        two_km_rides = list()
        forty_mins_rides = list()
        distance = list()
        leader_board = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_BOSCH_ODD_CHALLENGES_DATA)
        for result in results:
            name = result[0]
            challenges = result[1]
            challenges_data = result[2]

            if challenges:
                leader_board.append({"athlete_id": challenges_data['athlete_id'], "name": name,
                                     "location": challenges_data['location'],
                                     "points": challenges_data['c2w_rides_points'] + challenges_data[
                                         'c2w_distance_points'] + challenges_data['2x30_points'] + challenges_data[
                                                   '40x30_points'] + challenges_data['distance_points']})
                if "c2w_rides" in challenges['id']:
                    cycle_to_work_rides.append(
                        {'name': name, 'value': challenges_data['c2w_days'],
                         'points': challenges_data['c2w_rides_points'],
                         'rides': challenges_data['c2w_rides'], 'athlete_id': challenges_data['athlete_id'],
                         'location': challenges_data['location']})
                elif "c2w_distance" in challenges['id']:
                    cycle_to_work_distance.append(
                        {'name': name, 'value': challenges_data['c2w_distance_days'],
                         'points': challenges_data['c2w_distance_points'],
                         'rides': challenges_data['c2w_distance'], 'athlete_id': challenges_data['athlete_id'],
                         'location': challenges_data['location']})
                if "2x30" in challenges['id']:
                    two_km_rides.append(
                        {'name': name, 'value': challenges_data['2x30'], 'points': challenges_data['2x30_points'],
                         'athlete_id': challenges_data['athlete_id'], 'location': challenges_data['location']})
                elif "40x30" in challenges['id']:
                    forty_mins_rides.append(
                        {'name': name, 'value': challenges_data['40x30'], 'points': challenges_data['40x30_points'],
                         'athlete_id': challenges_data['athlete_id'], 'location': challenges_data['location']})
                elif "distance" in challenges['id']:
                    distance.append(
                        {'name': name, 'value': self.operations.meters_to_kilometers(challenges_data['distance']),
                         'points': challenges_data['distance_points'], 'athlete_id': challenges_data['athlete_id'],
                         'location': challenges_data['location']})

        c2w_rides_points_temp = sorted(cycle_to_work_rides, key=operator.itemgetter('points'), reverse=True)
        c2w_rides_distance_temp = sorted(cycle_to_work_distance, key=operator.itemgetter('points'), reverse=True)
        two_km_temp = sorted(two_km_rides, key=operator.itemgetter('points'), reverse=True)
        forty_mins_temp = sorted(forty_mins_rides, key=operator.itemgetter('points'), reverse=True)
        distance_temp = sorted(distance, key=operator.itemgetter('points'), reverse=True)
        leader_board_temp = sorted(leader_board, key=operator.itemgetter('points'), reverse=True)

        c2w_rides_points_sorted = list()
        rank = 1
        for athlete in c2w_rides_points_temp:
            c2w_rides_points_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'rides': athlete['rides'], 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        c2w_distance_points_sorted = list()
        rank = 1
        for athlete in c2w_rides_distance_temp:
            c2w_distance_points_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'rides': athlete['rides'], 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        two_km_rides_sorted = list()
        rank = 1
        for athlete in two_km_temp:
            two_km_rides_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        forty_mins_rides_sorted = list()
        rank = 1
        for athlete in forty_mins_temp:
            forty_mins_rides_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        distance_sorted = list()
        rank = 1
        for athlete in distance_temp:
            distance_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'distance': athlete['value'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        leader_board_sorted = list()
        rank = 1
        for athlete in leader_board_temp:
            leader_board_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        self.iron_cache_resource.put_cache("bosch_odd_challenges_result", "c2w_rides",
                                           ujson.dumps(c2w_rides_points_sorted))
        self.iron_cache_resource.put_cache("bosch_odd_challenges_result", "c2w_distance",
                                           ujson.dumps(c2w_distance_points_sorted))
        self.iron_cache_resource.put_cache("bosch_odd_challenges_result", "2x30",
                                           ujson.dumps(two_km_rides_sorted))
        self.iron_cache_resource.put_cache("bosch_odd_challenges_result", "30x40",
                                           ujson.dumps(forty_mins_rides_sorted))
        self.iron_cache_resource.put_cache("bosch_odd_challenges_result", "distance",
                                           ujson.dumps(distance_sorted))
        self.iron_cache_resource.put_cache("bosch_odd_challenges_result", "leader_board",
                                           ujson.dumps(leader_board_sorted))

    def main(self, athlete_details):
        if athlete_details['even_challenges']:
            self.even_challenges(athlete_details)
            self.consolidate_even_challenges_result()
        if athlete_details['odd_challenges']:
            self.odd_challenges(athlete_details)
            self.consolidate_odd_challenges_result()
        if athlete_details['bosch_even_challenges']:
            self.bosch_even_challenges(athlete_details)
            self.consolidate_bosch_even_challenges_result()
        if athlete_details['bosch_odd_challenges']:
            self.bosch_odd_challenges(athlete_details)
            self.consolidate_bosch_odd_challenges_result()
        if athlete_details['tok_odd_challenges']:
            self.tok_odd_month_challenge.tok_odd_challenges(athlete_details)
            self.tok_odd_month_challenge.consolidate_tok_odd_challenges_result()
