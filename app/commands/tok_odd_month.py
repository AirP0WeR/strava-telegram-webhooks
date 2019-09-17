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
from app.resources.strava import StravaResource
from app.resources.telegram import TelegramResource


class ToKOddMonth:
    def __init__(self):
        self.strava_resource = StravaResource()
        self.app_constants = AppConstants()
        self.app_variables = AppVariables()
        self.operations = Operations()
        self.database_resource = DatabaseResource()
        self.telegram_resource = TelegramResource()
        self.iron_cache_resource = IronCacheResource()

    def get_activity_type(self, activity):
        activity_type = None
        if activity.type == 'VirtualRide' or activity.type == 'Ride':
            activity_type = "Ride"
        elif activity.type == 'Run' or activity.type == 'VirtualRun':
            activity_type = "Run"
        elif activity.type == 'Swim':
            activity_type = "Swim"

        return activity_type

    def get_activities_calendar(self, athlete_details):
        activities_calendar = {"2019916": {"result": False, "data": {"activities": []}},
                               "2019917": {"result": False, "data": {"activities": []}},
                               "2019918": {"result": False, "data": {"activities": []}},
                               "2019919": {"result": False, "data": {"activities": []}},
                               "2019920": {"result": False, "data": {"activities": []}},
                               "2019921": {"result": False, "data": {"activities": []}},
                               "2019922": {"result": False, "data": {"activities": []}},
                               "2019923": {"result": False, "data": {"activities": []}},
                               "2019924": {"result": False, "data": {"activities": []}},
                               "2019925": {"result": False, "data": {"activities": []}},
                               "2019926": {"result": False, "data": {"activities": []}},
                               "2019927": {"result": False, "data": {"activities": []}},
                               "2019928": {"result": False, "data": {"activities": []}},
                               "2019929": {"result": False, "data": {"activities": []}},
                               "2019930": {"result": False, "data": {"activities": []}},
                               "2019101": {"result": False, "data": {"activities": []}},
                               "2019102": {"result": False, "data": {"activities": []}},
                               "2019103": {"result": False, "data": {"activities": []}},
                               "2019104": {"result": False, "data": {"activities": []}},
                               "2019105": {"result": False, "data": {"activities": []}},
                               "2019106": {"result": False, "data": {"activities": []}},
                               "2019107": {"result": False, "data": {"activities": []}},
                               "2019108": {"result": False, "data": {"activities": []}},
                               "2019109": {"result": False, "data": {"activities": []}},
                               "20191010": {"result": False, "data": {"activities": []}},
                               "20191011": {"result": False, "data": {"activities": []}},
                               "20191012": {"result": False, "data": {"activities": []}},
                               "20191013": {"result": False, "data": {"activities": []}},
                               "20191014": {"result": False, "data": {"activities": []}},
                               "20191015": {"result": False, "data": {"activities": []}},
                               "20191016": {"result": False, "activities": []},
                               "20191017": {"result": False, "data": {"activities": []}},
                               "20191018": {"result": False, "data": {"activities": []}},
                               "20191019": {"result": False, "data": {"activities": []}},
                               "20191020": {"result": False, "data": {"activities": []}},
                               "20191021": {"result": False, "data": {"activities": []}},
                               "20191022": {"result": False, "data": {"activities": []}},
                               "20191023": {"result": False, "data": {"activities": []}},
                               "20191024": {"result": False, "data": {"activities": []}},
                               "20191025": {"result": False, "data": {"activities": []}},
                               "20191026": {"result": False, "data": {"activities": []}},
                               "20191027": {"result": False, "data": {"activities": []}},
                               "20191028": {"result": False, "data": {"activities": []}},
                               "20191029": {"result": False, "data": {"activities": []}},
                               "20191030": {"result": False, "data": {"activities": []}},
                               "20191031": {"result": False, "data": {"activities": []}},
                               "2019111": {"result": False, "data": {"activities": []}},
                               "2019112": {"result": False, "data": {"activities": []}},
                               "2019113": {"result": False, "data": {"activities": []}},
                               "2019114": {"result": False, "data": {"activities": []}},
                               "2019115": {"result": False, "data": {"activities": []}},
                               "2019116": {"result": False, "data": {"activities": []}},
                               "2019117": {"result": False, "data": {"activities": []}},
                               "2019118": {"result": False, "data": {"activities": []}},
                               "2019119": {"result": False, "data": {"activities": []}},
                               "20191110": {"result": False, "data": {"activities": []}},
                               "20191111": {"result": False, "data": {"activities": []}},
                               "20191112": {"result": False, "data": {"activities": []}},
                               "20191113": {"result": False, "data": {"activities": []}},
                               "20191114": {"result": False, "data": {"activities": []}},
                               "20191115": {"result": False, "data": {"activities": []}},
                               "20191116": {"result": False, "data": {"activities": []}},
                               "20191117": {"result": False, "data": {"activities": []}},
                               "20191118": {"result": False, "data": {"activities": []}},
                               "20191119": {"result": False, "data": {"activities": []}},
                               "20191120": {"result": False, "data": {"activities": []}},
                               "20191121": {"result": False, "data": {"activities": []}},
                               "20191122": {"result": False, "data": {"activities": []}},
                               "20191123": {"result": False, "data": {"activities": []}},
                               "20191124": {"result": False, "data": {"activities": []}}}
        try:
            for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                    athlete_details['athlete_token'], self.app_variables.tok_odd_challenges_from_date,
                    self.app_variables.tok_odd_challenges_to_date):
                activity_type = activity.type
                activity_year = activity.start_date_local.year
                activity_month = activity.start_date_local.month
                activity_day = activity.start_date_local.day
                activity_distance = self.operations.meters_to_kilometers(float(activity.distance))
                activity_elevation = self.operations.remove_decimal_point(float(activity.total_elevation_gain))
                activity_time = unithelper.timedelta_to_seconds(activity.moving_time)
                calendar_key = "{activity_year}{activity_month}{activity_day}".format(activity_year=activity_year,
                                                                                      activity_month=activity_month,
                                                                                      activity_day=activity_day)
                logging.info(
                    "Type: %s | Year: %s | Month: %s | Day: %s | Distance: %s | Time: %s | Elevation: %s, Calendar Key: %s",
                    activity_type, activity_year, activity_month, activity_day, activity_distance, activity_time,
                    activity_elevation, calendar_key)
                if self.operations.supported_activities_for_tok_challenges(
                        activity) and activity_month in self.app_variables.tok_odd_challenges_month and activity_year in self.app_variables.tok_odd_challenges_year:
                    logging.info("Activity considered.")
                    activities_calendar[calendar_key]["result"] = True
                    activities_calendar[calendar_key]["data"]["activities"].append({
                        "type": self.get_activity_type(activity),
                        "distance": activity_distance,
                        "elevation": activity_elevation
                    })

        except ValueError as exception_message:
            if str(exception_message) == "day is out of range for month":
                logging.info("Future date")
            else:
                logging.info(exception_message)
        except Exception:
            logging.info(traceback.format_exc())
        finally:
            return ujson.dumps(activities_calendar)

    @staticmethod
    def calculate_activity_points(activities_calendar):
        activities_calendar = ujson.loads(activities_calendar)
        for activity_day in activities_calendar:
            if activity_day["result"]:
                for activity in activities_calendar[activity_day]["data"]["activities"]:
                    if activity["type"] == "Ride":
                        activity["activity_points"] = 2 if activity["distance"] >= 10000.0 else 0
                    elif activity["type"] == "Run":
                        activity["activity_points"] = 2 if activity["distance"] >= 1000.0 else 0
                    elif activity["type"] == "Swim":
                        activity["activity_points"] = 2 if activity["distance"] >= 500.0 else 0
        return activities_calendar

    def calculate_distance_bonus(self, activities_calendar):
        for activity_day in activities_calendar:
            for activity in activities_calendar[activity_day]["activities"]:
                if activity["type"] == "Ride":
                    activity["distance_bonus"] = 2 if activity["distance"] >= 10000.0 else 0
                elif activity["type"] == "Run":
                    activity["distance_bonus"] = 2 if activity["distance"] >= 1000.0 else 0
                elif activity["type"] == "Swim":
                    activity["distance_bonus"] = 2 if activity["distance"] >= 500.0 else 0
        return activities_calendar

    def temp(self):
        if activity_distance >= 100.0:
            ride_calendar[calendar_key]["bonus_distance_sot"] = 100
        elif activity_distance >= 50.0:
            ride_calendar[calendar_key]["bonus_distance_sot"] = 50 if ride_calendar[calendar_key][
                                                                          "bonus_distance_sot"] < 50 else \
                ride_calendar[calendar_key]["bonus_distance_sot"]
        elif activity_distance >= 25.0:
            ride_calendar[calendar_key]["bonus_distance_sot"] = 25 if ride_calendar[calendar_key][
                                                                          "bonus_distance_sot"] < 25 else \
                ride_calendar[calendar_key]["bonus_distance_sot"]

        if activity_elevation >= 2000:
            ride_calendar[calendar_key]["bonus_elevation_sot"] = 2000
        elif activity_elevation >= 1500:
            ride_calendar[calendar_key]["bonus_elevation_sot"] = 1500 if ride_calendar[calendar_key][
                                                                             "bonus_elevation_sot"] < 1500 else \
                ride_calendar[calendar_key]["bonus_elevation_sot"]
        elif activity_elevation >= 1000:
            ride_calendar[calendar_key]["bonus_elevation_sot"] = 1000 if ride_calendar[calendar_key][
                                                                             "bonus_elevation_sot"] < 1000 else \
                ride_calendar[calendar_key]["bonus_elevation_sot"]
        elif activity_elevation >= 500:
            ride_calendar[calendar_key]["bonus_elevation_sot"] = 500 if ride_calendar[calendar_key][
                                                                            "bonus_elevation_sot"] < 500 else \
                ride_calendar[calendar_key]["bonus_elevation_sot"]

    def tok_odd_challenges(self, athlete_details):
        logging.info("Calculating ToK odd challenges..")
        activities_calendar = self.get_activities_calendar(athlete_details)
        logging.info("Activities Calendar: %s", activities_calendar)
        activities_calendar = self.calculate_activity_points(activities_calendar)
        logging.info("Activities Calendar: %s", activities_calendar)
        # points = 0
        # points = self.calculate_base_points(points, activities_calendar)
        # for day in activities_calendar:
        #     # A cap of 100 kms(single ride) is set for base points.
        #     activities_calendar[day]["distance"] = activities_calendar[day]["distance"] if activities_calendar[day][
        #                                                                            "distance"] <= 150.0 else 150.0
        #     # A cap of 1500 meters(single ride) of elevation gain is set for base points.
        #     activities_calendar[day]["elevation"] = activities_calendar[day]["elevation"] if activities_calendar[day][
        #                                                                              "elevation"] <= 2000 else 2000
        #
        # logging.info("Ride Calendar: %s", activities_calendar)
        #
        # total_distance = 0.0
        # total_elevation = 0
        # total_activities = 0
        # total_hundreds = 0
        # total_fifties = 0
        # total_twenty_fives = 0
        #
        # for day in activities_calendar:
        #     total_distance += activities_calendar[day]["distance"]
        #     total_elevation += activities_calendar[day]["elevation"]
        #     total_activities += activities_calendar[day]["activities"]
        #     if activities_calendar[day]["bonus_distance_sot"] == 100:
        #         total_hundreds += 1
        #     elif activities_calendar[day]["bonus_distance_sot"] == 50:
        #         total_fifties += 1
        #     elif activities_calendar[day]["bonus_distance_sot"] == 25:
        #         total_twenty_fives += 1
        #
        # total_points = 0
        #
        # for day in activities_calendar:
        #     if activities_calendar[day]["bonus_distance_sot"] >= 100.0:
        #         total_points += 35
        #     elif activities_calendar[day]["bonus_distance_sot"] >= 50.0:
        #         total_points += 15
        #     elif activities_calendar[day]["bonus_distance_sot"] >= 25.0:
        #         total_points += 5
        #
        #     elif activities_calendar[day]["bonus_elevation_sot"] >= 2000:
        #         total_points += 60
        #     elif activities_calendar[day]["bonus_elevation_sot"] >= 1500:
        #         total_points += 40
        #     elif activities_calendar[day]["bonus_elevation_sot"] >= 1000:
        #         total_points += 25
        #     elif activities_calendar[day]["bonus_elevation_sot"] >= 500:
        #         total_points += 10
        #
        # # 10 km = 1 point
        # total_points += int(total_distance / 10)
        # # 100 meters = 1 point (Elevation gain)
        # total_points += int(total_elevation / 100)
        # # 1 activity = 1 point
        # total_points += total_activities
        # # 1000 kms in a month = 150 points
        # if total_distance >= 3000.0:
        #     total_points += 500
        # # 10000 meters of elevation gain in a month = 150 points
        # if total_elevation >= 35000:
        #     total_points += 500
        #
        # # 50 km for 5 successive days = 100 points*
        # # 100 km for 3 successive days = 100 points
        # hundreds_streak = 0
        # fifties_streak = 0
        # for day in activities_calendar:
        #     distance = activities_calendar[day]["bonus_distance_sot"]
        #     if distance == 100:
        #         hundreds_streak += 1
        #         fifties_streak += 1
        #     else:
        #         hundreds_streak = 0
        #         if distance == 50:
        #             fifties_streak += 1
        #         else:
        #             fifties_streak = 0
        #     if hundreds_streak == 3:
        #         total_points += 100
        #         hundreds_streak = 0
        #         fifties_streak = 0
        #     elif hundreds_streak == 2:
        #         total_points += 50
        #         hundreds_streak = 0
        #         fifties_streak = 0
        #     elif fifties_streak == 5:
        #         total_points += 50
        #         hundreds_streak = 0
        #         fifties_streak = 0
        #     elif fifties_streak == 3:
        #         total_points += 25
        #         hundreds_streak = 0
        #         fifties_streak = 0
        #
        # logging.info("total_distance: %s | total_elevation: %s, total_activities: %s | total_points: %s | "
        #              "total_hundreds: %s | total_fifties: %s | ride_calendar: %s | "
        #              "hundreds_streak: %s | fifties_streak: %s",
        #              total_distance, total_elevation, total_activities, total_points, total_hundreds, total_fifties,
        #              activities_calendar, hundreds_streak, fifties_streak)
        #
        # if self.database_resource.write_operation(self.app_constants.QUERY_UPDATE_TOK_ODD_CHALLENGES_DATA.format(
        #         challenges_data=ujson.dumps({'athlete_id': athlete_details['athlete_id'], 'points': total_points}),
        #         athlete_id=athlete_details['athlete_id'])):
        #     self.telegram_resource.send_message(
        #         "Updated ToK odd challenges data for {name}.".format(name=athlete_details['name']))
        # else:
        #     self.telegram_resource.send_message(
        #         "Failed to update ToK odd challenges data for {name}".format(name=athlete_details['name']))

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
