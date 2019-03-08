#  -*- encoding: utf-8 -*-

import logging

from app.common.constants_and_variables import AppConstants
from app.common.operations import Operations
from app.resources.strava import StravaResource
from app.resources.telegram import TelegramResource


class AutoUpdateIndoorRide(object):

    def __init__(self):
        self.app_constants = AppConstants()
        self.operations = Operations()
        self.strava_resource = StravaResource()
        self.telegram_resource = TelegramResource()

    @staticmethod
    def get_indoor_activity_name(athlete_details, activity):
        if athlete_details['update_indoor_ride_data']['name'] == 'Automatic':
            activity_hour = activity.start_date_local.hour
            if 3 <= activity_hour <= 11:
                athlete_details['update_indoor_ride_data']['name'] = "Morning Ride"
            elif 12 <= activity_hour <= 15:
                athlete_details['update_indoor_ride_data']['name'] = "Afternoon Ride"
            elif 16 <= activity_hour <= 18:
                athlete_details['update_indoor_ride_data']['name'] = "Evening Ride"
            elif (19 <= activity_hour <= 23) or (0 <= activity_hour <= 2):
                athlete_details['update_indoor_ride_data']['name'] = "Night Ride"

        return athlete_details

    def get_configured_update_indoor_ride_data(self, athlete_details):
        configured_data = self.app_constants.MESSAGE_UPDATED_INDOOR_RIDE
        if athlete_details['update_indoor_ride_data']['name']:
            configured_data += "\nActivity Name: {activity_name}".format(
                activity_name=athlete_details['update_indoor_ride_data']['name'])
        if athlete_details['update_indoor_ride_data']['gear_id']:
            bike_name = self.strava_resource.get_gear_name(athlete_details['athlete_token'],
                                                           athlete_details['update_indoor_ride_data']['gear_id'])
            configured_data += "\nBike: {bike_name}".format(bike_name=bike_name)

        return configured_data

    def main(self, activity, athlete_details):
        if self.operations.is_activity_a_ride(activity):
            if self.operations.is_indoor(activity):
                if athlete_details['update_indoor_ride']:
                    athlete_details = self.get_indoor_activity_name(athlete_details, activity)
                    result = self.strava_resource.update_strava_activity(athlete_details['athlete_token'],
                                                                         activity.id,
                                                                         athlete_details['update_indoor_ride_data'][
                                                                             'name'],
                                                                         athlete_details['update_indoor_ride_data'][
                                                                             'gear_id'])
                    if result:
                        message = self.get_configured_update_indoor_ride_data(athlete_details)
                    else:
                        message = "Error auto updating indoor ride."

                    self.telegram_resource.send_message(chat_id=athlete_details['chat_id'], message=message)
                    self.telegram_resource.shadow_message(message)
                else:
                    logging.info("Auto update indoor ride is not enabled.")
            else:
                logging.info("Activity is not an indoor ride.")
        else:
            logging.info("Activity Type is not Ride.")
