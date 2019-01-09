#  -*- encoding: utf-8 -*-

from stravalib.client import Client


class StravaClient(object):

    @staticmethod
    def get_client():
        strava_client = Client()
        return strava_client

    @staticmethod
    def get_client_with_token(athlete_token):
        strava_client = Client()
        strava_client.access_token = athlete_token
        return strava_client
