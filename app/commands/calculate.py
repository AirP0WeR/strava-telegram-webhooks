#  -*- encoding: utf-8 -*-

import logging
from datetime import date, datetime

from stravalib import unithelper

from app.common.operations import Operations
from app.resources.strava import StravaResource


class CalculateStats:

    def __init__(self, athlete_token):
        self.athlete_token = athlete_token
        self.operations = Operations()
        self.strava_resource = StravaResource()

    @staticmethod
    def get_rider_stats():
        return {
            "updated": "",
            "athlete_name": "",
            "athlete_strava_joined_date": "",
            "athlete_followers": 0,
            "athlete_following": 0,
            "ride_at_total": 0,
            "ride_at_indoor_total": 0,
            "ride_at_distance": 0,
            "ride_at_indoor_distance": 0,
            "ride_at_moving_time": 0,
            "ride_at_indoor_moving_time": 0,
            "ride_at_elevation_gain": 0,
            "ride_at_fifty": 0,
            "ride_at_hundred": 0,
            "ride_at_biggest_ride": 0,
            "ride_at_max_elevation_gain": 0,
            "ride_at_achievements": 0,
            "ride_at_commutes": 0,
            "ride_at_pr": 0,
            "ride_at_calories": 0,
            "ride_ytd_total": 0,
            "ride_ytd_indoor_total": 0,
            "ride_ytd_distance": 0,
            "ride_ytd_indoor_distance": 0,
            "ride_ytd_moving_time": 0,
            "ride_ytd_indoor_moving_time": 0,
            "ride_ytd_elevation_gain": 0,
            "ride_ytd_fifty": 0,
            "ride_ytd_hundred": 0,
            "ride_ytd_biggest_ride": 0,
            "ride_ytd_max_elevation_gain": 0,
            "ride_ytd_achievements": 0,
            "ride_ytd_commutes": 0,
            "ride_ytd_pr": 0,
            "ride_ytd_calories": 0,
            "ride_py_total": 0,
            "ride_py_indoor_total": 0,
            "ride_py_distance": 0,
            "ride_py_indoor_distance": 0,
            "ride_py_moving_time": 0,
            "ride_py_indoor_moving_time": 0,
            "ride_py_elevation_gain": 0,
            "ride_py_fifty": 0,
            "ride_py_hundred": 0,
            "ride_py_biggest_ride": 0,
            "ride_py_max_elevation_gain": 0,
            "ride_py_achievements": 0,
            "ride_py_commutes": 0,
            "ride_py_pr": 0,
            "ride_py_calories": 0,
            "ride_cm_total": 0,
            "ride_cm_indoor_total": 0,
            "ride_cm_distance": 0,
            "ride_cm_indoor_distance": 0,
            "ride_cm_moving_time": 0,
            "ride_cm_indoor_moving_time": 0,
            "ride_cm_elevation_gain": 0,
            "ride_cm_fifty": 0,
            "ride_cm_hundred": 0,
            "ride_cm_biggest_ride": 0,
            "ride_cm_max_elevation_gain": 0,
            "ride_cm_achievements": 0,
            "ride_cm_commutes": 0,
            "ride_cm_pr": 0,
            "ride_cm_calories": 0,
            "ride_pm_total": 0,
            "ride_pm_indoor_total": 0,
            "ride_pm_distance": 0,
            "ride_pm_indoor_distance": 0,
            "ride_pm_moving_time": 0,
            "ride_pm_indoor_moving_time": 0,
            "ride_pm_elevation_gain": 0,
            "ride_pm_fifty": 0,
            "ride_pm_hundred": 0,
            "ride_pm_biggest_ride": 0,
            "ride_pm_max_elevation_gain": 0,
            "ride_pm_achievements": 0,
            "ride_pm_commutes": 0,
            "ride_pm_pr": 0,
            "ride_pm_calories": 0,
            "run_at_total": 0,
            "run_at_indoor_total": 0,
            "run_at_distance": 0,
            "run_at_indoor_distance": 0,
            "run_at_moving_time": 0,
            "run_at_indoor_moving_time": 0,
            "run_at_elevation_gain": 0,
            "run_at_five": 0,
            "run_at_ten": 0,
            "run_at_hm": 0,
            "run_at_fm": 0,
            "run_at_ultra": 0,
            "run_at_biggest_run": 0,
            "run_at_max_elevation_gain": 0,
            "run_at_achievements": 0,
            "run_at_commutes": 0,
            "run_at_pr": 0,
            "run_at_calories": 0,
            "run_ytd_total": 0,
            "run_ytd_indoor_total": 0,
            "run_ytd_distance": 0,
            "run_ytd_indoor_distance": 0,
            "run_ytd_moving_time": 0,
            "run_ytd_indoor_moving_time": 0,
            "run_ytd_elevation_gain": 0,
            "run_ytd_five": 0,
            "run_ytd_ten": 0,
            "run_ytd_hm": 0,
            "run_ytd_fm": 0,
            "run_ytd_ultra": 0,
            "run_ytd_biggest_run": 0,
            "run_ytd_max_elevation_gain": 0,
            "run_ytd_achievements": 0,
            "run_ytd_commutes": 0,
            "run_ytd_pr": 0,
            "run_ytd_calories": 0,
            "run_py_total": 0,
            "run_py_indoor_total": 0,
            "run_py_distance": 0,
            "run_py_indoor_distance": 0,
            "run_py_moving_time": 0,
            "run_py_indoor_moving_time": 0,
            "run_py_elevation_gain": 0,
            "run_py_five": 0,
            "run_py_ten": 0,
            "run_py_hm": 0,
            "run_py_fm": 0,
            "run_py_ultra": 0,
            "run_py_biggest_run": 0,
            "run_py_max_elevation_gain": 0,
            "run_py_achievements": 0,
            "run_py_commutes": 0,
            "run_py_pr": 0,
            "run_py_calories": 0,
            "run_cm_total": 0,
            "run_cm_indoor_total": 0,
            "run_cm_distance": 0,
            "run_cm_indoor_distance": 0,
            "run_cm_moving_time": 0,
            "run_cm_indoor_moving_time": 0,
            "run_cm_elevation_gain": 0,
            "run_cm_five": 0,
            "run_cm_ten": 0,
            "run_cm_hm": 0,
            "run_cm_fm": 0,
            "run_cm_ultra": 0,
            "run_cm_biggest_run": 0,
            "run_cm_max_elevation_gain": 0,
            "run_cm_achievements": 0,
            "run_cm_commutes": 0,
            "run_cm_pr": 0,
            "run_cm_calories": 0,
            "run_pm_total": 0,
            "run_pm_indoor_total": 0,
            "run_pm_distance": 0,
            "run_pm_indoor_distance": 0,
            "run_pm_moving_time": 0,
            "run_pm_indoor_moving_time": 0,
            "run_pm_elevation_gain": 0,
            "run_pm_five": 0,
            "run_pm_ten": 0,
            "run_pm_hm": 0,
            "run_pm_fm": 0,
            "run_pm_ultra": 0,
            "run_pm_biggest_run": 0,
            "run_pm_max_elevation_gain": 0,
            "run_pm_achievements": 0,
            "run_pm_commutes": 0,
            "run_pm_pr": 0,
            "run_pm_calories": 0,
            "swim_at_total": 0,
            "swim_at_distance": 0,
            "swim_at_moving_time": 0,
            "swim_at_50": 0,
            "swim_at_100": 0,
            "swim_at_200": 0,
            "swim_at_400": 0,
            "swim_at_800": 0,
            "swim_at_1500": 0,
            "swim_at_biggest_swim": 0,
            "swim_at_achievements": 0,
            "swim_at_pr": 0,
            "swim_at_calories": 0,
            "swim_ytd_total": 0,
            "swim_ytd_distance": 0,
            "swim_ytd_moving_time": 0,
            "swim_ytd_50": 0,
            "swim_ytd_100": 0,
            "swim_ytd_200": 0,
            "swim_ytd_400": 0,
            "swim_ytd_800": 0,
            "swim_ytd_1500": 0,
            "swim_ytd_biggest_swim": 0,
            "swim_ytd_achievements": 0,
            "swim_ytd_pr": 0,
            "swim_ytd_calories": 0,
            "swim_py_total": 0,
            "swim_py_distance": 0,
            "swim_py_moving_time": 0,
            "swim_py_50": 0,
            "swim_py_100": 0,
            "swim_py_200": 0,
            "swim_py_400": 0,
            "swim_py_800": 0,
            "swim_py_1500": 0,
            "swim_py_biggest_swim": 0,
            "swim_py_achievements": 0,
            "swim_py_pr": 0,
            "swim_py_calories": 0,
            "swim_cm_total": 0,
            "swim_cm_distance": 0,
            "swim_cm_moving_time": 0,
            "swim_cm_50": 0,
            "swim_cm_100": 0,
            "swim_cm_200": 0,
            "swim_cm_400": 0,
            "swim_cm_800": 0,
            "swim_cm_1500": 0,
            "swim_cm_biggest_swim": 0,
            "swim_cm_achievements": 0,
            "swim_cm_pr": 0,
            "swim_cm_calories": 0,
            "swim_pm_total": 0,
            "swim_pm_distance": 0,
            "swim_pm_moving_time": 0,
            "swim_pm_50": 0,
            "swim_pm_100": 0,
            "swim_pm_200": 0,
            "swim_pm_400": 0,
            "swim_pm_800": 0,
            "swim_pm_1500": 0,
            "swim_pm_biggest_swim": 0,
            "swim_pm_achievements": 0,
            "swim_pm_pr": 0,
            "swim_pm_calories": 0,
        }

    def calculate(self):
        logging.info("Calculating stats..")
        athlete_info = self.strava_resource.get_athlete_info(self.athlete_token)
        activities = self.strava_resource.get_strava_activities_after_date(self.athlete_token, "1970-01-01T00:00:00Z")
        today_date = date.today()
        current_month = today_date.month
        previous_month = (current_month - 1) if (current_month > 1) else 12
        current_year = date.today().year
        previous_year = today_date.year - 1
        rider_stats = self.get_rider_stats()

        rider_stats["updated"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        rider_stats["athlete_name"] = "{first_name} {last_name}".format(first_name=athlete_info.firstname,
                                                                        last_name=athlete_info.lastname)
        rider_stats["athlete_strava_joined_date"] = athlete_info.created_at.date().strftime('%Y-%m-%d')
        rider_stats["athlete_followers"] = athlete_info.follower_count
        rider_stats["athlete_following"] = athlete_info.friend_count

        for activity in activities:
            if not self.operations.is_flagged(activity):
                distance = float(activity.distance)
                moving_time = unithelper.timedelta_to_seconds(activity.moving_time)
                total_elevation_gain = float(activity.total_elevation_gain)
                activity_year = activity.start_date_local.year
                activity_month = activity.start_date_local.month
                if self.operations.is_activity_a_ride(activity):
                    rider_stats["ride_at_total"] += 1
                    rider_stats["ride_at_distance"] += distance
                    rider_stats["ride_at_moving_time"] += moving_time
                    rider_stats["ride_at_elevation_gain"] += total_elevation_gain
                    rider_stats["ride_at_achievements"] += activity.achievement_count
                    rider_stats["ride_at_pr"] += activity.pr_count
                    if activity.kilojoules:
                        rider_stats["ride_at_calories"] += activity.kilojoules
                    if self.operations.is_indoor(activity):
                        rider_stats["ride_at_indoor_total"] += 1
                        rider_stats["ride_at_indoor_distance"] += distance
                        rider_stats["ride_at_indoor_moving_time"] += moving_time
                    if activity.commute:
                        rider_stats["ride_at_commutes"] += 1
                    if distance > rider_stats["ride_at_biggest_ride"]:
                        rider_stats["ride_at_biggest_ride"] = distance
                    if total_elevation_gain > rider_stats["ride_at_max_elevation_gain"]:
                        rider_stats["ride_at_max_elevation_gain"] = total_elevation_gain
                    if 50000.0 <= distance < 100000.0:
                        rider_stats["ride_at_fifty"] += 1
                    elif distance > 100000.0:
                        rider_stats["ride_at_hundred"] += 1
                elif self.operations.is_activity_a_run(activity):
                    rider_stats["run_at_total"] += 1
                    rider_stats["run_at_distance"] += distance
                    rider_stats["run_at_moving_time"] += moving_time
                    rider_stats["run_at_elevation_gain"] += total_elevation_gain
                    rider_stats["run_at_achievements"] += activity.achievement_count
                    rider_stats["run_at_pr"] += activity.pr_count
                    if activity.kilojoules:
                        rider_stats["run_at_calories"] += activity.kilojoules
                    if self.operations.is_indoor(activity):
                        rider_stats["run_at_indoor_total"] += 1
                        rider_stats["run_at_indoor_distance"] += distance
                        rider_stats["run_at_indoor_moving_time"] += moving_time
                    if activity.commute:
                        rider_stats["run_at_commutes"] += 1
                    if distance > rider_stats["run_at_biggest_run"]:
                        rider_stats["run_at_biggest_run"] = distance
                    if total_elevation_gain > rider_stats["run_at_max_elevation_gain"]:
                        rider_stats["run_at_max_elevation_gain"] = total_elevation_gain
                    if 5000.0 <= distance < 10000.0:
                        rider_stats["run_at_five"] += 1
                    elif 10000.0 <= distance < 21000.0:
                        rider_stats["run_at_ten"] += 1
                    elif 21000.0 <= distance < 42000.0:
                        rider_stats["run_at_hm"] += 1
                    elif 42000.0 <= distance < 44000.0:
                        rider_stats["run_at_fm"] += 1
                    elif distance > 44000.0:
                        rider_stats["run_at_ultra"] += 1
                elif self.operations.is_activity_a_swim(activity):
                    rider_stats["swim_at_total"] += 1
                    rider_stats["swim_at_distance"] += distance
                    rider_stats["swim_at_moving_time"] += moving_time
                    rider_stats["swim_at_achievements"] += activity.achievement_count
                    rider_stats["swim_at_pr"] += activity.pr_count
                    if activity.kilojoules:
                        rider_stats["swim_at_calories"] += activity.kilojoules
                    if distance > rider_stats["swim_at_biggest_swim"]:
                        rider_stats["swim_at_biggest_swim"] = distance
                    if 50.0 <= distance < 100.0:
                        rider_stats["swim_at_50"] += 1
                    elif 100.0 <= distance < 200.0:
                        rider_stats["swim_at_100"] += 1
                    elif 200.0 <= distance < 400.0:
                        rider_stats["swim_at_200"] += 1
                    elif 400.0 <= distance < 800.0:
                        rider_stats["swim_at_400"] += 1
                    elif 800.0 <= distance < 1500.0:
                        rider_stats["swim_at_800"] += 1
                    elif distance > 1500.0:
                        rider_stats["swim_at_1500"] += 1

                if activity_year == current_year:
                    if self.operations.is_activity_a_ride(activity):
                        rider_stats["ride_ytd_total"] += 1
                        rider_stats["ride_ytd_distance"] += distance
                        rider_stats["ride_ytd_moving_time"] += moving_time
                        rider_stats["ride_ytd_elevation_gain"] += total_elevation_gain
                        rider_stats["ride_ytd_achievements"] += activity.achievement_count
                        rider_stats["ride_ytd_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["ride_ytd_calories"] += activity.kilojoules
                        if self.operations.is_indoor(activity):
                            rider_stats["ride_ytd_indoor_total"] += 1
                            rider_stats["ride_ytd_indoor_distance"] += distance
                            rider_stats["ride_ytd_indoor_moving_time"] += moving_time
                        if activity.commute:
                            rider_stats["ride_ytd_commutes"] += 1
                        if distance > rider_stats["ride_ytd_biggest_ride"]:
                            rider_stats["ride_ytd_biggest_ride"] = distance
                        if total_elevation_gain > rider_stats["ride_ytd_max_elevation_gain"]:
                            rider_stats["ride_ytd_max_elevation_gain"] = total_elevation_gain
                        if 50000.0 <= distance < 100000.0:
                            rider_stats["ride_ytd_fifty"] += 1
                        elif distance > 100000.0:
                            rider_stats["ride_ytd_hundred"] += 1
                    elif self.operations.is_activity_a_run(activity):
                        rider_stats["run_ytd_total"] += 1
                        rider_stats["run_ytd_distance"] += distance
                        rider_stats["run_ytd_moving_time"] += moving_time
                        rider_stats["run_ytd_elevation_gain"] += total_elevation_gain
                        rider_stats["run_ytd_achievements"] += activity.achievement_count
                        rider_stats["run_ytd_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["run_ytd_calories"] += activity.kilojoules
                        if self.operations.is_indoor(activity):
                            rider_stats["run_ytd_indoor_total"] += 1
                            rider_stats["run_ytd_indoor_distance"] += distance
                            rider_stats["run_ytd_indoor_moving_time"] += moving_time
                        if activity.commute:
                            rider_stats["run_ytd_commutes"] += 1
                        if distance > rider_stats["run_ytd_biggest_run"]:
                            rider_stats["run_ytd_biggest_run"] = distance
                        if total_elevation_gain > rider_stats["run_ytd_max_elevation_gain"]:
                            rider_stats["run_ytd_max_elevation_gain"] = total_elevation_gain
                        if 5000.0 <= distance < 10000.0:
                            rider_stats["run_ytd_five"] += 1
                        elif 10000.0 <= distance < 21000.0:
                            rider_stats["run_ytd_ten"] += 1
                        elif 21000.0 <= distance < 42000.0:
                            rider_stats["run_ytd_hm"] += 1
                        elif 42000.0 <= distance < 44000.0:
                            rider_stats["run_ytd_fm"] += 1
                        elif distance > 44000.0:
                            rider_stats["run_ytd_ultra"] += 1
                    elif self.operations.is_activity_a_swim(activity):
                        rider_stats["swim_ytd_total"] += 1
                        rider_stats["swim_ytd_distance"] += distance
                        rider_stats["swim_ytd_moving_time"] += moving_time
                        rider_stats["swim_ytd_achievements"] += activity.achievement_count
                        rider_stats["swim_ytd_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["swim_ytd_calories"] += activity.kilojoules
                        if distance > rider_stats["swim_ytd_biggest_swim"]:
                            rider_stats["swim_ytd_biggest_swim"] = distance
                        if 50.0 <= distance < 100.0:
                            rider_stats["swim_ytd_50"] += 1
                        elif 100.0 <= distance < 200.0:
                            rider_stats["swim_ytd_100"] += 1
                        elif 200.0 <= distance < 400.0:
                            rider_stats["swim_ytd_200"] += 1
                        elif 400.0 <= distance < 800.0:
                            rider_stats["swim_ytd_400"] += 1
                        elif 800.0 <= distance < 1500.0:
                            rider_stats["swim_ytd_800"] += 1
                        elif distance > 1500.0:
                            rider_stats["swim_ytd_1500"] += 1

                if activity_year == previous_year:
                    if self.operations.is_activity_a_ride(activity):
                        rider_stats["ride_py_total"] += 1
                        rider_stats["ride_py_distance"] += distance
                        rider_stats["ride_py_moving_time"] += moving_time
                        rider_stats["ride_py_elevation_gain"] += total_elevation_gain
                        rider_stats["ride_py_achievements"] += activity.achievement_count
                        rider_stats["ride_py_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["ride_py_calories"] += activity.kilojoules
                        if self.operations.is_indoor(activity):
                            rider_stats["ride_py_indoor_total"] += 1
                            rider_stats["ride_py_indoor_distance"] += distance
                            rider_stats["ride_py_indoor_moving_time"] += moving_time
                        if activity.commute:
                            rider_stats["ride_py_commutes"] += 1
                        if distance > rider_stats["ride_py_biggest_ride"]:
                            rider_stats["ride_py_biggest_ride"] = distance
                        if total_elevation_gain > rider_stats["ride_py_max_elevation_gain"]:
                            rider_stats["ride_py_max_elevation_gain"] = total_elevation_gain
                        if 50000.0 <= distance < 100000.0:
                            rider_stats["ride_py_fifty"] += 1
                        elif distance > 100000.0:
                            rider_stats["ride_py_hundred"] += 1
                    elif self.operations.is_activity_a_run(activity):
                        rider_stats["run_py_total"] += 1
                        rider_stats["run_py_distance"] += distance
                        rider_stats["run_py_moving_time"] += moving_time
                        rider_stats["run_py_elevation_gain"] += total_elevation_gain
                        rider_stats["run_py_achievements"] += activity.achievement_count
                        rider_stats["run_py_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["run_py_calories"] += activity.kilojoules
                        if self.operations.is_indoor(activity):
                            rider_stats["run_py_indoor_total"] += 1
                            rider_stats["run_py_indoor_distance"] += distance
                            rider_stats["run_py_indoor_moving_time"] += moving_time
                        if activity.commute:
                            rider_stats["run_py_commutes"] += 1
                        if distance > rider_stats["run_py_biggest_run"]:
                            rider_stats["run_py_biggest_run"] = distance
                        if total_elevation_gain > rider_stats["run_py_max_elevation_gain"]:
                            rider_stats["run_py_max_elevation_gain"] = total_elevation_gain
                        if 5000.0 <= distance < 10000.0:
                            rider_stats["run_py_five"] += 1
                        elif 10000.0 <= distance < 21000.0:
                            rider_stats["run_py_ten"] += 1
                        elif 21000.0 <= distance < 42000.0:
                            rider_stats["run_py_hm"] += 1
                        elif 42000.0 <= distance < 44000.0:
                            rider_stats["run_py_fm"] += 1
                        elif distance > 44000.0:
                            rider_stats["run_py_ultra"] += 1
                    elif self.operations.is_activity_a_swim(activity):
                        rider_stats["swim_py_total"] += 1
                        rider_stats["swim_py_distance"] += distance
                        rider_stats["swim_py_moving_time"] += moving_time
                        rider_stats["swim_py_achievements"] += activity.achievement_count
                        rider_stats["swim_py_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["swim_py_calories"] += activity.kilojoules
                        if distance > rider_stats["swim_py_biggest_swim"]:
                            rider_stats["swim_py_biggest_swim"] = distance
                        if 50.0 <= distance < 100.0:
                            rider_stats["swim_py_50"] += 1
                        elif 100.0 <= distance < 200.0:
                            rider_stats["swim_py_100"] += 1
                        elif 200.0 <= distance < 400.0:
                            rider_stats["swim_py_200"] += 1
                        elif 400.0 <= distance < 800.0:
                            rider_stats["swim_py_400"] += 1
                        elif 800.0 <= distance < 1500.0:
                            rider_stats["swim_py_800"] += 1
                        elif distance > 1500.0:
                            rider_stats["swim_py_1500"] += 1

                if activity_month == current_month and activity_year == current_year:
                    if self.operations.is_activity_a_ride(activity):
                        rider_stats["ride_cm_total"] += 1
                        rider_stats["ride_cm_distance"] += distance
                        rider_stats["ride_cm_moving_time"] += moving_time
                        rider_stats["ride_cm_elevation_gain"] += total_elevation_gain
                        rider_stats["ride_cm_achievements"] += activity.achievement_count
                        rider_stats["ride_cm_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["ride_cm_calories"] += activity.kilojoules
                        if self.operations.is_indoor(activity):
                            rider_stats["ride_cm_indoor_total"] += 1
                            rider_stats["ride_cm_indoor_distance"] += distance
                            rider_stats["ride_cm_indoor_moving_time"] += moving_time
                        if activity.commute:
                            rider_stats["ride_cm_commutes"] += 1
                        if distance > rider_stats["ride_cm_biggest_ride"]:
                            rider_stats["ride_cm_biggest_ride"] = distance
                        if total_elevation_gain > rider_stats["ride_cm_max_elevation_gain"]:
                            rider_stats["ride_cm_max_elevation_gain"] = total_elevation_gain
                        if 50000.0 <= distance < 100000.0:
                            rider_stats["ride_cm_fifty"] += 1
                        elif distance > 100000.0:
                            rider_stats["ride_cm_hundred"] += 1
                    elif self.operations.is_activity_a_run(activity):
                        rider_stats["run_cm_total"] += 1
                        rider_stats["run_cm_distance"] += distance
                        rider_stats["run_cm_moving_time"] += moving_time
                        rider_stats["run_cm_elevation_gain"] += total_elevation_gain
                        rider_stats["run_cm_achievements"] += activity.achievement_count
                        rider_stats["run_cm_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["run_cm_calories"] += activity.kilojoules
                        if self.operations.is_indoor(activity):
                            rider_stats["run_cm_indoor_total"] += 1
                            rider_stats["run_cm_indoor_distance"] += distance
                            rider_stats["run_cm_indoor_moving_time"] += moving_time
                        if activity.commute:
                            rider_stats["run_cm_commutes"] += 1
                        if distance > rider_stats["run_cm_biggest_run"]:
                            rider_stats["run_cm_biggest_run"] = distance
                        if total_elevation_gain > rider_stats["run_cm_max_elevation_gain"]:
                            rider_stats["run_cm_max_elevation_gain"] = total_elevation_gain
                        if 5000.0 <= distance < 10000.0:
                            rider_stats["run_cm_five"] += 1
                        elif 10000.0 <= distance < 21000.0:
                            rider_stats["run_cm_ten"] += 1
                        elif 21000.0 <= distance < 42000.0:
                            rider_stats["run_cm_hm"] += 1
                        elif 42000.0 <= distance < 44000.0:
                            rider_stats["run_cm_fm"] += 1
                        elif distance > 44000.0:
                            rider_stats["run_cm_ultra"] += 1
                    elif self.operations.is_activity_a_swim(activity):
                        rider_stats["swim_cm_total"] += 1
                        rider_stats["swim_cm_distance"] += distance
                        rider_stats["swim_cm_moving_time"] += moving_time
                        rider_stats["swim_cm_achievements"] += activity.achievement_count
                        rider_stats["swim_cm_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["swim_cm_calories"] += activity.kilojoules
                        if distance > rider_stats["swim_cm_biggest_swim"]:
                            rider_stats["swim_cm_biggest_swim"] = distance
                        if 50.0 <= distance < 100.0:
                            rider_stats["swim_cm_50"] += 1
                        elif 100.0 <= distance < 200.0:
                            rider_stats["swim_cm_100"] += 1
                        elif 200.0 <= distance < 400.0:
                            rider_stats["swim_cm_200"] += 1
                        elif 400.0 <= distance < 800.0:
                            rider_stats["swim_cm_400"] += 1
                        elif 800.0 <= distance < 1500.0:
                            rider_stats["swim_cm_800"] += 1
                        elif distance > 1500.0:
                            rider_stats["swim_cm_1500"] += 1

                # TODO This condition fails for January. Fix it.
                if activity_month == previous_month and activity_year == current_year:
                    if self.operations.is_activity_a_ride(activity):
                        rider_stats["ride_pm_total"] += 1
                        rider_stats["ride_pm_distance"] += distance
                        rider_stats["ride_pm_moving_time"] += moving_time
                        rider_stats["ride_pm_elevation_gain"] += total_elevation_gain
                        rider_stats["ride_pm_achievements"] += activity.achievement_count
                        rider_stats["ride_pm_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["ride_pm_calories"] += activity.kilojoules
                        if self.operations.is_indoor(activity):
                            rider_stats["ride_pm_indoor_total"] += 1
                            rider_stats["ride_pm_indoor_distance"] += distance
                            rider_stats["ride_pm_indoor_moving_time"] += moving_time
                        if activity.commute:
                            rider_stats["ride_pm_commutes"] += 1
                        if distance > rider_stats["ride_pm_biggest_ride"]:
                            rider_stats["ride_pm_biggest_ride"] = distance
                        if total_elevation_gain > rider_stats["ride_pm_max_elevation_gain"]:
                            rider_stats["ride_pm_max_elevation_gain"] = total_elevation_gain
                        if 50000.0 <= distance < 100000.0:
                            rider_stats["ride_pm_fifty"] += 1
                        elif distance > 100000.0:
                            rider_stats["ride_pm_hundred"] += 1
                    elif self.operations.is_activity_a_run(activity):
                        rider_stats["run_pm_total"] += 1
                        rider_stats["run_pm_distance"] += distance
                        rider_stats["run_pm_moving_time"] += moving_time
                        rider_stats["run_pm_elevation_gain"] += total_elevation_gain
                        rider_stats["run_pm_achievements"] += activity.achievement_count
                        rider_stats["run_pm_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["run_pm_calories"] += activity.kilojoules
                        if self.operations.is_indoor(activity):
                            rider_stats["run_pm_indoor_total"] += 1
                            rider_stats["run_pm_indoor_distance"] += distance
                            rider_stats["run_pm_indoor_moving_time"] += moving_time
                        if activity.commute:
                            rider_stats["run_pm_commutes"] += 1
                        if distance > rider_stats["run_pm_biggest_run"]:
                            rider_stats["run_pm_biggest_run"] = distance
                        if total_elevation_gain > rider_stats["run_pm_max_elevation_gain"]:
                            rider_stats["run_pm_max_elevation_gain"] = total_elevation_gain
                        if 5000.0 <= distance < 10000.0:
                            rider_stats["run_pm_five"] += 1
                        elif 10000.0 <= distance < 21000.0:
                            rider_stats["run_pm_ten"] += 1
                        elif 21000.0 <= distance < 42000.0:
                            rider_stats["run_pm_hm"] += 1
                        elif 42000.0 <= distance < 44000.0:
                            rider_stats["run_pm_fm"] += 1
                        elif distance > 44000.0:
                            rider_stats["run_pm_ultra"] += 1
                    elif self.operations.is_activity_a_swim(activity):
                        rider_stats["swim_pm_total"] += 1
                        rider_stats["swim_pm_distance"] += distance
                        rider_stats["swim_pm_moving_time"] += moving_time
                        rider_stats["swim_pm_achievements"] += activity.achievement_count
                        rider_stats["swim_pm_pr"] += activity.pr_count
                        if activity.kilojoules:
                            rider_stats["swim_pm_calories"] += activity.kilojoules
                        if distance > rider_stats["swim_pm_biggest_swim"]:
                            rider_stats["swim_pm_biggest_swim"] = distance
                        if 50.0 <= distance < 100.0:
                            rider_stats["swim_pm_50"] += 1
                        elif 100.0 <= distance < 200.0:
                            rider_stats["swim_pm_100"] += 1
                        elif 200.0 <= distance < 400.0:
                            rider_stats["swim_pm_200"] += 1
                        elif 400.0 <= distance < 800.0:
                            rider_stats["swim_pm_400"] += 1
                        elif 800.0 <= distance < 1500.0:
                            rider_stats["swim_pm_800"] += 1
                        elif distance > 1500.0:
                            rider_stats["swim_pm_1500"] += 1

        return rider_stats
