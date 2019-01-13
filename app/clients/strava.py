#  -*- encoding: utf-8 -*-

import logging
import time
from os import sys, path

import psycopg2
import requests
from stravalib.client import Client

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from app.common.constants_and_variables import AppConstants, AppVariables


class StravaClient(object):

    def __init__(self):
        self.bot_constants = AppConstants()
        self.bot_variables = AppVariables()

    @staticmethod
    def get_client():
        strava_client = Client()
        return strava_client

    @staticmethod
    def get_client_with_token(athlete_token):
        strava_client = Client()
        strava_client.access_token = athlete_token
        return strava_client

    def refresh_and_update_token(self, athlete_id, refresh_token):
        response = requests.post(self.bot_constants.API_TOKEN_EXCHANGE, data={
            'client_id': int(self.bot_variables.client_id),
            'client_secret': self.bot_variables.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }).json()

        access_info = dict()
        access_info['access_token'] = response['access_token']
        access_info['refresh_token'] = response['refresh_token']
        access_info['expires_at'] = response['expires_at']

        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.bot_constants.QUERY_UPDATE_TOKEN.format(
            access_token=access_info['access_token'],
            refresh_token=access_info['refresh_token'],
            expires_at=access_info['expires_at'],
            athlete_id=athlete_id
        ))
        cursor.close()
        database_connection.commit()
        database_connection.close()

        return response['access_token']

    def get_athlete_token(self, athlete_id):
        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.bot_constants.QUERY_FETCH_TOKEN.format(athlete_id=athlete_id))
        result = cursor.fetchall()
        cursor.close()
        database_connection.close()
        if len(result) > 0:
            access_token = result[0][0]
            refresh_token = result[0][1]
            expires_at = result[0][2]
            current_time = int(time.time())
            if current_time > expires_at:
                logging.info(
                    "Token has expired | Current Time: {current_time} | Token Expiry Time: {expires_at}".format(
                        current_time=current_time, expires_at=expires_at))
                access_token = self.refresh_and_update_token(athlete_id, refresh_token)
                return access_token
            else:
                logging.info(
                    "Token is still valid | Current Time: {current_time} | Token Expiry Time: {expires_at}".format(
                        current_time=current_time, expires_at=expires_at))
                return access_token
        else:
            return False
