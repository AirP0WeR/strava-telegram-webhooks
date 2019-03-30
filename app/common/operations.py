#  -*- encoding: utf-8 -*-

import datetime
from decimal import Decimal, ROUND_DOWN


class Operations(object):

    @staticmethod
    def meters_to_kilometers(distance):
        return float((Decimal(distance / 1000.0)).quantize(Decimal('.1'), rounding=ROUND_DOWN))

    @staticmethod
    def remove_decimal_point(number):
        return int(number)

    @staticmethod
    def round_off_two_decimal_places(number):
        return str(round(number, 2))

    @staticmethod
    def seconds_to_human_readable(time_in_seconds):
        return str(datetime.timedelta(seconds=time_in_seconds))

    @staticmethod
    def strava_activity_hyperlink():
        return "[{text}](https://www.strava.com/activities/{activity_id})"

    @staticmethod
    def is_flagged(activity):
        return True if activity.flagged else False

    @staticmethod
    def is_activity_a_ride(activity):
        return True if (activity.type == 'Ride' or activity.type == 'VirtualRide') else False

    @staticmethod
    def is_activity_a_run(activity):
        return True if (activity.type == 'Run' or activity.type == 'VirtualRun') else False

    @staticmethod
    def is_activity_a_swim(activity):
        return True if activity.type == 'Swim' else False

    @staticmethod
    def is_indoor(activity):
        return True if (activity.trainer or activity.type == 'VirtualRide' or activity.type == 'VirtualRun') else False

    @staticmethod
    def supported_activities(activity):
        return True if (activity.type == 'VirtualRide'
                        or activity.type == 'VirtualRun'
                        or activity.type == 'Ride'
                        or activity.type == 'Run'
                        or activity.type == 'Swim') else False

    @staticmethod
    def supported_activities_for_challenges(activity):
        return True if (activity.type == 'VirtualRide' or activity.type == 'Ride') else False
