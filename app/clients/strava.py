#  -*- encoding: utf-8 -*-

from stravalib.client import Client


class StravaClient:

    @staticmethod
    def get_client(athlete_token):
        strava_client = Client()
        strava_client.access_token = athlete_token
        return strava_client
