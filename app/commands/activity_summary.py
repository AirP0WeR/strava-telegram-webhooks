#  -*- encoding: utf-8 -*-

import logging

from stravalib import unithelper

from app.common.constants_and_variables import AppConstants
from app.common.operations import Operations
from app.resources.strava import StravaResource
from app.resources.telegram import TelegramResource


class ActivitySummary:

    def __init__(self):
        self.app_constants = AppConstants()
        self.operations = Operations()
        self.strava_resource = StravaResource()
        self.telegram_resource = TelegramResource()

    def generate_activity_summary_for_supported_activities(self, activity, athlete_details):
        activity_summary = "*New Activity Summary*:\n\n" \
                           "Athlete Name: {athlete_name}\n" \
                           "Activity: [{activity_name}](https://www.strava.com/activities/{activity_id})\n" \
                           "Activity Date: {activity_date}\n" \
                           "Activity Type: {activity_type}\n\n" \
                           "Distance: {distance} km\n" \
                           "Moving Time: {moving_time}\n" \
                           "Elapsed Time: {elapsed_time}\n" \
                           "Calories: {calories}\n".format(
            athlete_name=athlete_details['name'],
            activity_name=activity.name,
            activity_id=activity.id,
            activity_type=activity.type,
            activity_date=activity.start_date_local,
            distance=self.operations.meters_to_kilometers(float(activity.distance)),
            moving_time=self.operations.seconds_to_human_readable(
                unithelper.timedelta_to_seconds(activity.moving_time)),
            elapsed_time=self.operations.seconds_to_human_readable(
                unithelper.timedelta_to_seconds(activity.elapsed_time)),
            calories=self.operations.remove_decimal_point(activity.calories))

        if self.operations.is_activity_a_ride(activity):
            activity_summary += "Avg Speed: {avg_speed}\n" \
                                "Max Speed: {max_speed}\n".format(
                avg_speed=unithelper.kilometers_per_hour(activity.average_speed),
                max_speed=unithelper.kilometers_per_hour(activity.max_speed))
        else:
            activity_summary += "Avg Pace: {avg_pace}\n" \
                                "Max Pace: {max_pace}\n".format(
                avg_pace=unithelper.kilometers_per_hour(activity.average_speed),
                max_pace=unithelper.kilometers_per_hour(activity.max_speed))

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

        return activity_summary

    def main(self, activity, athlete_details):
        if athlete_details['enable_activity_summary']:
            activity_summary = self.generate_activity_summary_for_supported_activities(activity, athlete_details)
            self.telegram_resource.send_message(chat_id=athlete_details['chat_id'], message=activity_summary)
            self.telegram_resource.shadow_message(activity_summary)
        else:
            logging.info("Activity Summary is not enabled.")
