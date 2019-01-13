#  -*- encoding: utf-8 -*-

from os import sys, path

from stravalib.client import Client

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from app.common.constants_and_variables import AppConstants, AppVariables


class StravaClient(object):

    def __init__(self):
        self.bot_constants = AppConstants()
        self.bot_variables = AppVariables()

    @staticmethod
    def get_client_with_token(athlete_token):
        strava_client = Client()
        strava_client.access_token = athlete_token
        return strava_client
