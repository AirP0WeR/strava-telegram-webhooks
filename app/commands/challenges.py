#  -*- encoding: utf-8 -*-
import logging
import operator
import traceback
from collections import defaultdict
from math import radians, sin, cos, asin, sqrt

import ujson
from stravalib import unithelper

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
            self.calculate_challenges_stats.consolidate_even_challenges_result()
            self.calculate_challenges_stats.consolidate_odd_challenges_result()
            self.calculate_challenges_stats.consolidate_bosch_even_challenges_result()
            self.calculate_challenges_stats.consolidate_bosch_odd_challenges_result()

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
                                 '6x15': True if details['id'] == '6x15' else False,
                                 '30x30': True if details['id'] == '30x30' else False,
                                 'distance': True if details['id'] == 'distance' else False})

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

    @staticmethod
    def dummy_function():
        pass

    def get_challenges_result(self, company, month, challenge):
        challenges_result = False

        companies = ['cadence90', 'bosch']
        months = ['odd', 'even']
        challenges = ['leaderboard', 'c2w', '6_km', '30_min', 'distance', 'leader_board']

        if company in companies and month in months and challenge in challenges:

            consolidate_results_options = defaultdict(lambda: self.dummy_function, {
                'bosch_even': self.calculate_challenges_stats.consolidate_bosch_even_challenges_result,
                'cadence90_odd': self.calculate_challenges_stats.consolidate_odd_challenges_result,
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

        even_challenges = athlete_details['even_challenges']
        for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                athlete_details['athlete_token'], self.app_variables.even_challenges_from_date,
                self.app_variables.even_challenges_to_date):
            logging.info("Type: %s | Month: %s | Year: %s | Day: %s | Distance: %s | Total Elevation Gain: %s",
                         activity.type, activity.start_date_local.month, activity.start_date_local.year,
                         activity.start_date_local.day, float(activity.distance), float(activity.total_elevation_gain))
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
            "Even Ride Calendar: %s | Even Rides Count : %s | Even Total Distance: %s | Even Total Elevation: %s",
            even_challenges_ride_calendar, even_challenges_rides_count, even_challenges_total_distance,
            even_challenges_total_elevation)

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
            self.telegram_resource.send_message(
                "Updated even challenges data for {name}.".format(name=athlete_details['name']))
        else:
            self.telegram_resource.send_message(
                "Failed to update even challenges data for {name}".format(name=athlete_details['name']))

    def odd_challenges(self, athlete_details):
        cadence90_odd_challenges = athlete_details['odd_challenges']
        if cadence90_odd_challenges and cadence90_odd_challenges['payment']:
            odd_challenges_stats = {'points': 0}
            if self.database_resource.write_operation(self.app_constants.QUERY_UPDATE_ODD_CHALLENGES_DATA.format(
                    odd_challenges_data=ujson.dumps(odd_challenges_stats), athlete_id=athlete_details['athlete_id'])):
                self.telegram_resource.send_message(
                    "Updated Cadence90 odd month challenge data for {name}.".format(name=athlete_details['name']))
            else:
                self.telegram_resource.send_message(
                    "Failed to update Cadence90 odd month challenge data for {name}".format(
                        name=athlete_details['name']))

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
        six_km_rides = 0
        six_km_points = 0
        is_eligible_for_six_km_rides_bonus = False

        thirty_min_rides = 0
        thirty_min_points = 0
        is_eligible_for_thirty_mins_rides_bonus = False

        total_distance = 0.0
        is_eligible_for_distance_bonus = False

        cycle_to_work_calendar = {
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
        cycle_to_work_rides = 0
        cycle_to_work_points = 0

        challenges = athlete_details['bosch_even_challenges']

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
                activity.type, activity_month, activity_year, activity_day, activity_distance, activity_time, start_gps,
                end_gps)
            if self.operations.supported_activities_for_challenges(activity) and not self.operations.is_indoor(
                    activity) and activity_month == self.app_variables.even_challenges_month and activity_year == self.app_variables.even_challenges_year:
                if start_gps and end_gps:
                    is_eligible_to, is_eligible_from = self.is_c2w_eligible(start_gps, end_gps)
                    if is_eligible_to:
                        cycle_to_work_calendar[activity_day]['to'] = True
                        cycle_to_work_rides += 1
                        cycle_to_work_points += 30
                    if is_eligible_from:
                        cycle_to_work_calendar[activity_day]['from'] = True
                        cycle_to_work_rides += 1
                        cycle_to_work_points += 30
                if activity_distance >= 6000.0:
                    six_km_rides += 1
                    six_km_points += 6
                    if activity_distance >= 25000.0:
                        is_eligible_for_six_km_rides_bonus = True
                if activity_time >= 1800:
                    thirty_min_rides += 1
                    thirty_min_points += 6
                    if activity_time >= 10800:
                        is_eligible_for_thirty_mins_rides_bonus = True
                total_distance += activity_distance
                if activity_distance >= 150000.0:
                    is_eligible_for_distance_bonus = True

        logging.info("Total distance: %s | 6 km rides : %s | 30 min rides: %s | Cycle to Work Calendar: %s",
                     total_distance, six_km_rides, thirty_min_rides, cycle_to_work_calendar)

        challenges_stats = {
            'c2w': 0,
            'c2w_rides': 0,
            'c2w_points': 0,
            '6x15': 0,
            '6x15_points': 0,
            '30x30': 0,
            '30x30_points': 0,
            'distance': 0.0,
            'distance_points': 0,
            'athlete_id': athlete_details['athlete_id'],
            'location': challenges['location']
        }

        for day in cycle_to_work_calendar:
            if cycle_to_work_calendar[day]['to'] and cycle_to_work_calendar[day]['from']:
                challenges_stats['c2w'] += 1

        challenges_stats['c2w_rides'] += cycle_to_work_rides
        challenges_stats['c2w_points'] += cycle_to_work_points
        challenges_stats['c2w_points'] = 300 if cycle_to_work_points >= 300 else cycle_to_work_points
        if cycle_to_work_rides >= 1:
            challenges_stats['c2w_points'] += 50
        if cycle_to_work_rides >= 2:
            challenges_stats['c2w_points'] += 50
        if challenges_stats['c2w'] >= 12:
            challenges_stats['c2w_points'] += 100

        if challenges['id'] == '6x15':
            challenges_stats['6x15'] += six_km_rides
            challenges_stats['6x15_points'] = 180 if six_km_points >= 180 else six_km_points
            if six_km_rides >= 15:
                challenges_stats['6x15_points'] += 20
                if is_eligible_for_six_km_rides_bonus:
                    challenges_stats['6x15_points'] += 50

        elif challenges['id'] == '30x30':
            challenges_stats['30x30'] += thirty_min_rides
            challenges_stats['30x30_points'] = 180 if thirty_min_points >= 180 else thirty_min_points
            if thirty_min_rides >= 30:
                challenges_stats['30x30_points'] += 20
                if is_eligible_for_thirty_mins_rides_bonus:
                    challenges_stats['30x30_points'] += 50

        elif challenges['id'] == 'distance':
            challenges_stats['distance'] += total_distance
            distance_points = (int((total_distance / 1000.0) / 30.0)) * 6.0
            challenges_stats['distance_points'] = 180 if distance_points >= 180 else distance_points
            if total_distance >= 1000000.0:
                challenges_stats['distance_points'] += 20
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
        cycle_to_work = list()
        six_km_rides = list()
        thirty_mins_rides = list()
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
                                     "points": challenges_data['c2w_points'] + challenges_data['6x15_points'] +
                                               challenges_data['30x30_points'] + challenges_data['distance_points']})
                cycle_to_work.append(
                    {'name': name, 'value': challenges_data['c2w'], 'points': challenges_data['c2w_points'],
                     'rides': challenges_data['c2w_rides'], 'athlete_id': challenges_data['athlete_id'],
                     'location': challenges_data['location']})
                if challenges['id'] == '6x15':
                    six_km_rides.append(
                        {'name': name, 'value': challenges_data['6x15'], 'points': challenges_data['6x15_points'],
                         'athlete_id': challenges_data['athlete_id'], 'location': challenges_data['location']})
                elif challenges['id'] == '30x30':
                    thirty_mins_rides.append(
                        {'name': name, 'value': challenges_data['30x30'], 'points': challenges_data['30x30_points'],
                         'athlete_id': challenges_data['athlete_id'], 'location': challenges_data['location']})
                elif challenges['id'] == 'distance':
                    distance.append(
                        {'name': name, 'value': self.operations.meters_to_kilometers(challenges_data['distance']),
                         'points': challenges_data['distance_points'], 'athlete_id': challenges_data['athlete_id'],
                         'location': challenges_data['location']})

        bosch_even_challenge_c2w_points_temp = sorted(cycle_to_work, key=operator.itemgetter('points'), reverse=True)
        bosch_even_challenge_six_km_temp = sorted(six_km_rides, key=operator.itemgetter('points'), reverse=True)
        bosch_even_challenge_30_mins_temp = sorted(thirty_mins_rides, key=operator.itemgetter('points'),
                                                   reverse=True)
        bosch_even_challenge_distance_temp = sorted(distance, key=operator.itemgetter('points'), reverse=True)
        leader_board_temp = sorted(leader_board, key=operator.itemgetter('points'), reverse=True)

        c2w_points_sorted = list()
        rank = 1
        for athlete in bosch_even_challenge_c2w_points_temp:
            c2w_points_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'rides': athlete['rides'], 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        six_km_rides_sorted = list()
        rank = 1
        for athlete in bosch_even_challenge_six_km_temp:
            six_km_rides_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        thirty_mins_rides_sorted = list()
        rank = 1
        for athlete in bosch_even_challenge_30_mins_temp:
            thirty_mins_rides_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'count': athlete['value'], 'points': athlete['points'],
                 'athlete_id': athlete['athlete_id'], 'location': athlete['location']})
            rank += 1

        distance_sorted = list()
        rank = 1
        for athlete in bosch_even_challenge_distance_temp:
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

        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "c2w",
                                           ujson.dumps(c2w_points_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "6_km",
                                           ujson.dumps(six_km_rides_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "30_min",
                                           ujson.dumps(thirty_mins_rides_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "distance",
                                           ujson.dumps(distance_sorted))
        self.iron_cache_resource.put_cache("bosch_even_challenges_result", "leader_board",
                                           ujson.dumps(leader_board_sorted))

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
        self.telegram_resource.send_message("Updated cache for even challenges.")

    def consolidate_odd_challenges_result(self):
        odd_challenge = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_ODD_CHALLENGES_DATA)
        for result in results:
            name = result[0]
            challenges = result[1]
            challenges_data = result[2]

            if challenges and challenges['payment']:
                odd_challenge.append({'name': name, 'value': challenges_data['points']})

        odd_challenge_twenty_temp = sorted(odd_challenge, key=operator.itemgetter('value'), reverse=True)

        odd_challenge_sorted = list()
        rank = 1
        for athlete in odd_challenge_twenty_temp:
            odd_challenge_sorted.append(
                {'rank': rank, 'name': athlete['name'], 'value': athlete['value']})
            rank += 1

        if len(odd_challenge_sorted) == 0:
            odd_challenge_sorted.append({'rank': '', 'name': '', 'value': ''})

        self.iron_cache_resource.put_cache("cadence90_odd_challenges_result", "leaderboard",
                                           ujson.dumps(odd_challenge_sorted))
        self.telegram_resource.send_message("Updated cache for Cadence90 odd month challenges.")

    def bosch_odd_challenges(self, athlete_details):
        cycle_to_work_calendar = {
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
        cycle_to_work_rides = 0
        cycle_to_work_points = 0

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
        cycle_to_work_distance_distance = 0
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
                        cycle_to_work_calendar[activity_day]['to'] = True
                        cycle_to_work_rides += 1
                        cycle_to_work_points += 20
                        cycle_to_work_distance_calendar[activity_day]['to'] = activity_distance
                        cycle_to_work_distance_distance += activity_distance
                        cycle_to_work_distance_points += int(activity_distance / 1000)
                    if is_eligible_from:
                        cycle_to_work_calendar[activity_day]['from'] = True
                        cycle_to_work_rides += 1
                        cycle_to_work_points += 20
                        cycle_to_work_distance_calendar[activity_day]['from'] = activity_distance
                        cycle_to_work_distance_distance += activity_distance
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
            total_distance, two_km_rides, forty_min_rides, cycle_to_work_calendar,
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
            for day in cycle_to_work_calendar:
                if cycle_to_work_calendar[day]['to'] and cycle_to_work_calendar[day]['from']:
                    challenges_stats['c2w_days'] += 1

            challenges_stats['c2w_rides'] += cycle_to_work_rides
            challenges_stats['c2w_rides_points'] += cycle_to_work_points
            challenges_stats['c2w_rides_points'] = 500 if cycle_to_work_points > 500 else cycle_to_work_points
            if cycle_to_work_rides >= 1:
                challenges_stats['c2w_rides_points'] += 50
            if cycle_to_work_rides >= 2:
                challenges_stats['c2w_rides_points'] += 50
            if challenges_stats['c2w_days'] >= 15:
                challenges_stats['c2w_rides_points'] += 100

        elif "c2w_distance" in challenges['id']:
            for day in cycle_to_work_distance_calendar:
                if cycle_to_work_distance_calendar[day]['to'] > 0.0 and cycle_to_work_distance_calendar[day][
                    'from'] > 0.0:
                    challenges_stats['c2w_distance_days'] += 1

            challenges_stats['c2w_distance'] += cycle_to_work_distance_distance
            challenges_stats['c2w_distance_points'] += cycle_to_work_distance_points
            challenges_stats[
                'c2w_distance_points'] = 500 if cycle_to_work_distance_points > 500 else cycle_to_work_distance_points
            if cycle_to_work_rides >= 1:
                challenges_stats['c2w_distance_points'] += 50
            if cycle_to_work_rides >= 2:
                challenges_stats['c2w_distance_points'] += 50
            if challenges_stats['c2w_distance_points'] >= 500:
                challenges_stats['c2w_distance_points'] += 100

        if "2x30" in challenges['id']:
            challenges_stats['2x30'] += two_km_rides
            challenges_stats['2x30_points'] = two_km_points
            challenges_stats['2x30_points'] = 450 if two_km_points > 450 else two_km_points
            if cycle_to_work_rides >= 1:
                challenges_stats['2x30_points'] += 50
            if cycle_to_work_rides >= 2:
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
                        {'name': name, 'value': challenges_data['c2w_distance_days'],
                         'points': challenges_data['c2w_distance_points'],
                         'rides': challenges_data['c2w_rides'], 'athlete_id': challenges_data['athlete_id'],
                         'location': challenges_data['location']})
                elif "c2w_distance" in challenges['id']:
                    cycle_to_work_distance.append(
                        {'name': name, 'value': challenges_data['c2w_days'],
                         'points': challenges_data['c2w_rides_points'],
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
