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
        activities_calendar = {"calendar": {"2019916": {"result": False, "data": {"activities": []}},
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
                                            "20191124": {"result": False, "data": {"activities": []}}}}
        try:
            for activity in self.strava_resource.get_strava_activities_after_date_before_date(
                    athlete_details['athlete_token'], self.app_variables.tok_odd_challenges_from_date,
                    self.app_variables.tok_odd_challenges_to_date):
                activity_type = activity.type
                activity_year = activity.start_date_local.year
                activity_month = activity.start_date_local.month
                activity_day = activity.start_date_local.day
                activity_distance = float(activity.distance)
                activity_elevation = float(activity.total_elevation_gain)
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
                    activities_calendar["calendar"][calendar_key]["result"] = True
                    activities_calendar["calendar"][calendar_key]["data"]["activities"].append({
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
    def cap_ride_distance_and_elevation(activities_calendar):
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                for activity in activities_calendar["calendar"][activity_day]["data"]["activities"]:
                    if activity["type"] == "Ride":
                        activity["distance"] = activity["distance"] if activity["distance"] < 150000.0 else 150000.0
                        activity["elevation"] = activity["elevation"] if activity["elevation"] < 2000.0 else 2000.0
        return activities_calendar

    @staticmethod
    def calculate_activity_points(activities_calendar):
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                for activity in activities_calendar["calendar"][activity_day]["data"]["activities"]:
                    if activity["type"] == "Ride":
                        activity["activity_points"] = 2 if activity["distance"] >= 10000.0 else 0
                    elif activity["type"] == "Run":
                        activity["activity_points"] = 2 if activity["distance"] >= 1000.0 else 0
                    elif activity["type"] == "Swim":
                        activity["activity_points"] = 2 if activity["distance"] >= 500.0 else 0
        return activities_calendar

    @staticmethod
    def calculate_distance_bonus(activities_calendar):
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                for activity in activities_calendar["calendar"][activity_day]["data"]["activities"]:
                    if activity["type"] == "Ride":
                        if activity["distance"] >= 100000.0:
                            activity["distance_bonus_points"] = 35
                        elif activity["distance"] >= 50000.0:
                            activity["distance_bonus_points"] = 15
                        elif activity["distance"] >= 25000.0:
                            activity["distance_bonus_points"] = 5
                        else:
                            activity["distance_bonus_points"] = 0
                    elif activity["type"] == "Run":
                        if activity["distance"] >= 40000.0:
                            activity["distance_bonus_points"] = 35
                        elif activity["distance"] >= 20000.0:
                            activity["distance_bonus_points"] = 16
                        elif activity["distance"] >= 15000.0:
                            activity["distance_bonus_points"] = 12
                        elif activity["distance"] >= 10000.0:
                            activity["distance_bonus_points"] = 7
                        elif activity["distance"] >= 5000.0:
                            activity["distance_bonus_points"] = 3
                        else:
                            activity["distance_bonus_points"] = 0
                    elif activity["type"] == "Swim":
                        if activity["distance"] >= 2000.0:
                            activity["distance_bonus_points"] = 10
                        elif activity["distance"] >= 1500.0:
                            activity["distance_bonus_points"] = 5
                        elif activity["distance"] >= 1000.0:
                            activity["distance_bonus_points"] = 3
                        else:
                            activity["distance_bonus_points"] = 0
        return activities_calendar

    @staticmethod
    def calculate_elevation_bonus(activities_calendar):
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                for activity in activities_calendar["calendar"][activity_day]["data"]["activities"]:
                    if activity["type"] == "Ride":
                        if activity["elevation"] >= 2000.0:
                            activity["elevation_bonus_points"] = 60
                        elif activity["elevation"] >= 1500.0:
                            activity["elevation_bonus_points"] = 40
                        elif activity["elevation"] >= 1000.0:
                            activity["elevation_bonus_points"] = 25
                        elif activity["elevation"] >= 500.0:
                            activity["elevation_bonus_points"] = 10
                        else:
                            activity["elevation_bonus_points"] = 0
                    elif activity["type"] == "Run":
                        activity["elevation_bonus_points"] = 0
                    elif activity["type"] == "Swim":
                        activity["elevation_bonus_points"] = 0
        return activities_calendar

    @staticmethod
    def calculate_total_distance_and_elevation_for_the_day(activities_calendar):
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                activities_calendar["calendar"][activity_day]["data"].update(
                    {"distance": {"Ride": 0.0, "Run": 0.0, "Swim": 0.0}})
                activities_calendar["calendar"][activity_day]["data"].update(
                    {"elevation": {"Ride": 0.0, "Run": 0.0, "Swim": 0.0}})
                for activity in activities_calendar["calendar"][activity_day]["data"]["activities"]:
                    if activity["type"] == "Ride":
                        activities_calendar["calendar"][activity_day]["data"]["distance"]["Ride"] += activity[
                            "distance"]
                        activities_calendar["calendar"][activity_day]["data"]["elevation"]["Ride"] += activity[
                            "elevation"]
                    elif activity["type"] == "Run":
                        activities_calendar["calendar"][activity_day]["data"]["distance"]["Run"] += activity["distance"]
                        activities_calendar["calendar"][activity_day]["data"]["elevation"]["Run"] += activity[
                            "elevation"]
                    elif activity["type"] == "Swim":
                        activities_calendar["calendar"][activity_day]["data"]["distance"]["Swim"] += activity[
                            "distance"]
                        activities_calendar["calendar"][activity_day]["data"]["elevation"]["Swim"] += activity[
                            "elevation"]

        return activities_calendar

    @staticmethod
    def calculate_max_distance_and_elevation_for_the_day(activities_calendar):
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                activities_calendar["calendar"][activity_day]["data"].update(
                    {"max_distance": {"Ride": 0.0, "Run": 0.0, "Swim": 0.0}})
                activities_calendar["calendar"][activity_day]["data"].update(
                    {"max_elevation": {"Ride": 0.0, "Run": 0.0, "Swim": 0.0}})
                list_max_distance_ride = list()
                list_max_distance_run = list()
                list_max_distance_swim = list()
                list_max_elevation_ride = list()
                list_max_elevation_run = list()
                list_max_elevation_swim = list()
                for activity in activities_calendar["calendar"][activity_day]["data"]["activities"]:
                    if activity["type"] == "Ride":
                        list_max_distance_ride.append(activity["distance"])
                        list_max_elevation_ride.append(activity["elevation"])
                    elif activity["type"] == "Run":
                        list_max_distance_run.append(activity["distance"])
                        list_max_elevation_run.append(activity["elevation"])
                    elif activity["type"] == "Swim":
                        list_max_distance_swim.append(activity["distance"])
                        list_max_elevation_swim.append(activity["elevation"])

                activities_calendar["calendar"][activity_day]["data"]["max_distance"]["Ride"] = max(
                    list_max_distance_ride) if len(list_max_distance_ride) > 0 else 0
                activities_calendar["calendar"][activity_day]["data"]["max_distance"]["Run"] = max(
                    list_max_distance_run) if len(list_max_distance_run) > 0 else 0
                activities_calendar["calendar"][activity_day]["data"]["max_distance"]["Swim"] = max(
                    list_max_distance_swim) if len(list_max_distance_swim) > 0 else 0
                activities_calendar["calendar"][activity_day]["data"]["max_elevation"]["Ride"] = max(
                    list_max_elevation_ride) if len(list_max_elevation_ride) > 0 else 0
                activities_calendar["calendar"][activity_day]["data"]["max_elevation"]["Run"] = max(
                    list_max_elevation_run) if len(list_max_elevation_run) > 0 else 0
                activities_calendar["calendar"][activity_day]["data"]["max_elevation"]["Swim"] = max(
                    list_max_elevation_swim) if len(list_max_elevation_swim) > 0 else 0

        return activities_calendar

    @staticmethod
    def calculate_total_distance_and_elevation(activities_calendar):
        activities_calendar.update({"total_distance": {"Ride": 0.0, "Run": 0.0, "Swim": 0.0}})
        activities_calendar.update({"total_elevation": {"Ride": 0.0, "Run": 0.0, "Swim": 0.0}})
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                activities_calendar["total_distance"]["Ride"] += \
                activities_calendar["calendar"][activity_day]["data"]["distance"]["Ride"]
                activities_calendar["total_distance"]["Run"] += \
                activities_calendar["calendar"][activity_day]["data"]["distance"]["Run"]
                activities_calendar["total_distance"]["Swim"] += \
                activities_calendar["calendar"][activity_day]["data"]["distance"]["Swim"]
                activities_calendar["total_elevation"]["Ride"] += \
                activities_calendar["calendar"][activity_day]["data"]["elevation"]["Ride"]
                activities_calendar["total_elevation"]["Run"] += \
                activities_calendar["calendar"][activity_day]["data"]["elevation"]["Run"]
                activities_calendar["total_elevation"]["Swim"] += \
                activities_calendar["calendar"][activity_day]["data"]["elevation"]["Swim"]

        return activities_calendar

    @staticmethod
    def calculate_consecutive_fifties_and_hundreds(activities_calendar):
        activities_calendar.update({"consecutives": {
            "hundreds": {
                "three": 0,
                "two": 0
            },
            "fifties": {
                "five": 0,
                "three": 0
            }
        }})

        hundreds_streak = 0
        fifties_streak = 0
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                max_distance = activities_calendar["calendar"][activity_day]["data"]["max_distance"]["Ride"]
                if max_distance >= 100000.0:
                    hundreds_streak += 1
                    fifties_streak += 1
                else:
                    hundreds_streak = 0
                    if max_distance >= 50000.0:
                        fifties_streak += 1
                    else:
                        fifties_streak = 0

                if hundreds_streak == 3:
                    activities_calendar["consecutives"]["hundreds"]["three"] += 1
                    hundreds_streak = 0
                    fifties_streak = 0
                elif hundreds_streak == 2:
                    activities_calendar["consecutives"]["hundreds"]["two"] += 1
                    hundreds_streak = 0
                    fifties_streak = 0
                elif fifties_streak == 5:
                    activities_calendar["consecutives"]["fifties"]["five"] += 1
                    hundreds_streak = 0
                    fifties_streak = 0
                elif fifties_streak == 3:
                    activities_calendar["consecutives"]["fifties"]["three"] += 1
                    hundreds_streak = 0
                    fifties_streak = 0
            else:
                hundreds_streak = 0
                fifties_streak = 0

        return activities_calendar

    def calculate_base_points(self, points, activities_calendar):
        points["base"]["Ride"]["distance"] = int(
            self.operations.meters_to_kilometers(activities_calendar["total_distance"]["Ride"] / 10))
        points["base"]["Run"]["distance"] = int(
            self.operations.meters_to_kilometers(activities_calendar["total_distance"]["Run"]))
        points["base"]["Swim"]["distance"] = int(activities_calendar["total_distance"]["Swim"] / 500)
        points["base"]["Ride"]["elevation"] = int(activities_calendar["total_elevation"]["Ride"] / 100)
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                for activity in activities_calendar["calendar"][activity_day]["data"]["activities"]:
                    points["base"]["Ride"]["activities"] += activity["activity_points"]
        return points

    @staticmethod
    def calculate_bonus_points(points, activities_calendar):
        if activities_calendar["total_distance"]["Ride"] >= 3000000.0:
            points["bonus"]["Ride"]["total_distance"] = 500
        if activities_calendar["total_elevation"]["Ride"] >= 35000.0:
            points["bonus"]["Ride"]["total_elevation"] = 500
        for activity_day in activities_calendar["calendar"]:
            if activities_calendar["calendar"][activity_day]["result"]:
                for activity in activities_calendar["calendar"][activity_day]["data"]["activities"]:
                    if activity["type"] == "Ride":
                        points["bonus"]["Ride"]["distance"] += activity["distance_bonus_points"]
                        points["bonus"]["Ride"]["elevation"] += activity["elevation_bonus_points"]
                    elif activity["type"] == "Run":
                        points["bonus"]["Run"]["distance"] += activity["distance_bonus_points"]
                    elif activity["type"] == "Swim":
                        points["bonus"]["Swim"]["distance"] += activity["distance_bonus_points"]
        points["bonus"]["Ride"]["three_consecutive_hundreds"] = 100 * activities_calendar["consecutives"]["hundreds"][
            "three"]
        points["bonus"]["Ride"]["two_consecutive_hundreds"] = 50 * activities_calendar["consecutives"]["hundreds"][
            "two"]
        points["bonus"]["Ride"]["five_consecutive_fifties"] = 50 * activities_calendar["consecutives"]["fifties"][
            "five"]
        points["bonus"]["Ride"]["three_consecutive_fifties"] = 25 * activities_calendar["consecutives"]["fifties"][
            "three"]

        return points

    @staticmethod
    def calculate_total_points(points):
        total_points = list()
        total_points.append(sum(list(points["base"]["Ride"].values())))
        total_points.append(sum(list(points["base"]["Run"].values())))
        total_points.append(sum(list(points["base"]["Swim"].values())))
        total_points.append(sum(list(points["bonus"]["Ride"].values())))
        total_points.append(sum(list(points["bonus"]["Run"].values())))
        total_points.append(sum(list(points["bonus"]["Swim"].values())))
        return total_points

    def tok_odd_challenges(self, athlete_details):
        logging.info("Calculating ToK odd challenges..")
        activities_calendar = ujson.loads(self.get_activities_calendar(athlete_details))
        logging.info("Activities Calendar: %s", activities_calendar)
        activities_calendar = self.cap_ride_distance_and_elevation(activities_calendar)
        logging.info("Activities Calendar with capped distance and elevation for Rides: %s", activities_calendar)
        activities_calendar = self.calculate_activity_points(activities_calendar)
        logging.info("Activities Calendar with activity points: %s", activities_calendar)
        activities_calendar = self.calculate_distance_bonus(activities_calendar)
        logging.info("Activities Calendar with distance bonus: %s", activities_calendar)
        activities_calendar = self.calculate_elevation_bonus(activities_calendar)
        logging.info("Activities Calendar with elevation bonus: %s", activities_calendar)
        activities_calendar = self.calculate_total_distance_and_elevation_for_the_day(activities_calendar)
        logging.info("Activities Calendar with total distance and elevation for the day: %s", activities_calendar)
        activities_calendar = self.calculate_max_distance_and_elevation_for_the_day(activities_calendar)
        logging.info("Activities Calendar with max distance slot for the day: %s", activities_calendar)
        activities_calendar = self.calculate_total_distance_and_elevation(activities_calendar)
        logging.info("Activities Calendar with total distance and elevation: %s", activities_calendar)
        activities_calendar = self.calculate_consecutive_fifties_and_hundreds(activities_calendar)
        logging.info("Activities Calendar with consecutive fifties and hundreds: %s", activities_calendar)

        points = {
            "base": {
                "Ride": {
                    "distance": 0,
                    "elevation": 0,
                    "activities": 0
                },
                "Run": {
                    "distance": 0
                },
                "Swim": {
                    "distance": 0
                }
            },
            "bonus": {
                "Ride": {
                    "distance": 0,
                    "elevation": 0,
                    "total_distance": 0,
                    "total_elevation": 0,
                    "three_consecutive_hundreds": 0,
                    "two_consecutive_hundreds": 0,
                    "five_consecutive_fifties": 0,
                    "three_consecutive_fifties": 0
                },
                "Run": {
                    "distance": 0
                },
                "Swim": {
                    "distance": 0
                }
            }
        }
        points = self.calculate_base_points(points, activities_calendar)
        logging.info("Points with base: %s", points)

        points = self.calculate_bonus_points(points, activities_calendar)
        logging.info("Points with bonus: %s", points)

        total_points = self.calculate_total_points(points)
        logging.info("Total points: %s", total_points)

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
