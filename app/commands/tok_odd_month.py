#  -*- encoding: utf-8 -*-
import logging
import operator
import traceback

import ujson
from stravalib import unithelper

from app.common.constants_and_variables import AppConstants, AppVariables
from app.common.operations import Operations
from app.resources.database import DatabaseResource
from app.resources.iron_cache import IronCacheResource
from app.resources.telegram import TelegramResource
from resources.strava import StravaResource


class ToKOddMonth:
    def __init__(self):
        self.strava_resource = StravaResource()
        self.app_constants = AppConstants()
        self.app_variables = AppVariables()
        self.operations = Operations()
        self.database_resource = DatabaseResource()
        self.telegram_resource = TelegramResource()
        self.iron_cache_resource = IronCacheResource()

    def tok_odd_challenges(self, athlete_details):
        logging.info("Calculating ToK odd challenges..")
        ride_calendar = {
            201991: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            201992: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            201993: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            201994: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            201995: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            201996: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            201997: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            201998: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            201999: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                     "bonus_elevation_sot": 0},
            2019910: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019911: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019912: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019913: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019914: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019915: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019916: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019917: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019918: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019919: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019920: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019921: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019922: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019923: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019924: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019925: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019926: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019927: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019928: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019929: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019930: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019931: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019101: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019102: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019103: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019104: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019105: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019106: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019107: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019108: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019109: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            20191010: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191011: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191012: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191013: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191014: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191015: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191016: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191017: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191018: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191019: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191020: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191021: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191022: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191023: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191024: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191025: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191026: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191027: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191028: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191029: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191030: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191031: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            2019111: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019112: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019113: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019114: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019115: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019116: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019117: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019118: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            2019119: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                      "bonus_elevation_sot": 0},
            20191110: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191111: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191112: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191113: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191114: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191115: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191116: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191117: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191118: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191119: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191120: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191121: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191122: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191123: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191124: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191125: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191126: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191127: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191128: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191129: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191130: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0},
            20191131: {"distance": 0.0, "elevation": 0, "activities": 0, "bonus_distance_sot": 0,
                       "bonus_elevation_sot": 0}
        }

        try:
            for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                    athlete_details['athlete_token'], self.app_variables.tok_odd_challenges_from_date,
                    self.app_variables.tok_odd_challenges_to_date):
                activity_month = activity.start_date_local.month
                activity_year = activity.start_date_local.year
                activity_day = activity.start_date_local.day
                activity_distance = self.operations.meters_to_kilometers(float(activity.distance))
                activity_elevation = self.operations.remove_decimal_point(float(activity.total_elevation_gain))
                activity_time = unithelper.timedelta_to_seconds(activity.moving_time)
                calendar_day = int(
                    "{activity_year}{activity_month}{activity_day}".format(activity_year=activity_year,
                                                                           activity_month=activity_month,
                                                                           activity_day=activity_day))
                logging.info(
                    "Type: %s | Month: %s | Year: %s | Day: %s | Distance: %s | Time: %s | Elevation: %s, Calendar_day: %s",
                    activity.type, activity_month, activity_year, activity_day, activity_distance, activity_time,
                    activity_elevation, calendar_day)
                if self.operations.supported_activities_for_challenges(
                        activity) and activity_month in self.app_variables.tok_odd_challenges_month and activity_year in self.app_variables.tok_odd_challenges_year:

                    ride_calendar[calendar_day]["distance"] += activity_distance
                    ride_calendar[calendar_day]["elevation"] += activity_elevation
                    # Minimum 30 mins or 10 kms for 1 activity
                    if activity_time >= 1800 or activity_distance >= 10.0:
                        ride_calendar[calendar_day]["activities"] += 1

                    if activity_distance >= 100.0:
                        ride_calendar[calendar_day]["bonus_distance_sot"] = 100
                    elif activity_distance >= 50.0:
                        ride_calendar[calendar_day]["bonus_distance_sot"] = 50 if ride_calendar[calendar_day][
                                                                                      "bonus_distance_sot"] < 50 else \
                            ride_calendar[calendar_day]["bonus_distance_sot"]
                    elif activity_distance >= 25.0:
                        ride_calendar[calendar_day]["bonus_distance_sot"] = 25 if ride_calendar[calendar_day][
                                                                                      "bonus_distance_sot"] < 25 else \
                            ride_calendar[calendar_day]["bonus_distance_sot"]

                    if activity_elevation >= 2000:
                        ride_calendar[calendar_day]["bonus_elevation_sot"] = 2000
                    elif activity_elevation >= 1500:
                        ride_calendar[calendar_day]["bonus_elevation_sot"] = 1500 if ride_calendar[calendar_day][
                                                                                         "bonus_elevation_sot"] < 1500 else \
                            ride_calendar[calendar_day]["bonus_elevation_sot"]
                    elif activity_elevation >= 1000:
                        ride_calendar[calendar_day]["bonus_elevation_sot"] = 1000 if ride_calendar[calendar_day][
                                                                                         "bonus_elevation_sot"] < 1000 else \
                            ride_calendar[calendar_day]["bonus_elevation_sot"]
                    elif activity_elevation >= 500:
                        ride_calendar[calendar_day]["bonus_elevation_sot"] = 500 if ride_calendar[calendar_day][
                                                                                        "bonus_elevation_sot"] < 500 else \
                            ride_calendar[calendar_day]["bonus_elevation_sot"]

        except ValueError as exception_message:
            if str(exception_message) == "day is out of range for month":
                logging.info("Future date")
            else:
                logging.info(exception_message)
        except Exception:
            logging.info(traceback.format_exc())

        logging.info("Ride Calendar: %s", ride_calendar)

        for day in ride_calendar:
            # A cap of 100 kms(single ride) is set for base points.
            ride_calendar[day]["distance"] = ride_calendar[day]["distance"] if ride_calendar[day][
                                                                                   "distance"] <= 150.0 else 150.0
            # A cap of 1500 meters(single ride) of elevation gain is set for base points.
            ride_calendar[day]["elevation"] = ride_calendar[day]["elevation"] if ride_calendar[day][
                                                                                     "elevation"] <= 2000 else 2000

        logging.info("Ride Calendar: %s", ride_calendar)

        total_distance = 0.0
        total_elevation = 0
        total_activities = 0
        total_hundreds = 0
        total_fifties = 0
        total_twenty_fives = 0

        for day in ride_calendar:
            total_distance += ride_calendar[day]["distance"]
            total_elevation += ride_calendar[day]["elevation"]
            total_activities += ride_calendar[day]["activities"]
            if ride_calendar[day]["bonus_distance_sot"] == 100:
                total_hundreds += 1
            elif ride_calendar[day]["bonus_distance_sot"] == 50:
                total_fifties += 1
            elif ride_calendar[day]["bonus_distance_sot"] == 25:
                total_twenty_fives += 1

        total_points = 0

        for day in ride_calendar:
            if ride_calendar[day]["bonus_distance_sot"] >= 100.0:
                total_points += 35
            elif ride_calendar[day]["bonus_distance_sot"] >= 50.0:
                total_points += 15
            elif ride_calendar[day]["bonus_distance_sot"] >= 25.0:
                total_points += 5

            elif ride_calendar[day]["bonus_elevation_sot"] >= 2000:
                total_points += 60
            elif ride_calendar[day]["bonus_elevation_sot"] >= 1500:
                total_points += 40
            elif ride_calendar[day]["bonus_elevation_sot"] >= 1000:
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
        if total_distance >= 3000.0:
            total_points += 500
        # 10000 meters of elevation gain in a month = 150 points
        if total_elevation >= 35000:
            total_points += 500

        # 50 km for 5 successive days = 100 points*
        # 100 km for 3 successive days = 100 points
        hundreds_streak = 0
        fifties_streak = 0
        for day in ride_calendar:
            distance = ride_calendar[day]["bonus_distance_sot"]
            if distance == 100:
                hundreds_streak += 1
                fifties_streak += 1
            else:
                hundreds_streak = 0
                if distance == 50:
                    fifties_streak += 1
                else:
                    fifties_streak = 0
            if hundreds_streak == 3:
                total_points += 100
                hundreds_streak = 0
                fifties_streak = 0
            elif hundreds_streak == 2:
                total_points += 50
                hundreds_streak = 0
                fifties_streak = 0
            elif fifties_streak == 5:
                total_points += 50
                hundreds_streak = 0
                fifties_streak = 0
            elif fifties_streak == 3:
                total_points += 25
                hundreds_streak = 0
                fifties_streak = 0

        logging.info("total_distance: %s | total_elevation: %s, total_activities: %s | total_points: %s | "
                     "total_hundreds: %s | total_fifties: %s | ride_calendar: %s | "
                     "hundreds_streak: %s | fifties_streak: %s",
                     total_distance, total_elevation, total_activities, total_points, total_hundreds, total_fifties,
                     ride_calendar, hundreds_streak, fifties_streak)

        if self.database_resource.write_operation(self.app_constants.QUERY_UPDATE_TOK_ODD_CHALLENGES_DATA.format(
                challenges_data=ujson.dumps({'athlete_id': athlete_details['athlete_id'], 'points': total_points}),
                athlete_id=athlete_details['athlete_id'])):
            self.telegram_resource.send_message(
                "Updated ToK odd challenges data for {name}.".format(name=athlete_details['name']))
        else:
            self.telegram_resource.send_message(
                "Failed to update ToK odd challenges data for {name}".format(name=athlete_details['name']))

    def consolidate_tok_odd_challenges_result(self):
        odd_challenge = list()

        results = self.database_resource.read_all_operation(self.app_constants.QUERY_GET_TOK_ODD_CHALLENGES_DATA)
        for result in results:
            name = result[0]
            challenges = result[1]
            challenges_data = result[2]

            if challenges:
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

        self.iron_cache_resource.put_cache("tok_odd_challenges_result", "leaderboard",
                                           ujson.dumps(odd_challenge_sorted))
        self.telegram_resource.send_message("Updated cache for ToK odd month challenge.")
