#  -*- encoding: utf-8 -*-

import json
import logging
import time
from os import sys, path

import psycopg2
import requests

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from app.commands.calculate import CalculateStats
from app.common.constants_and_variables import AppConstants, AppVariables
from app.common.operations import Operations


class ProcessStats(object):

    def __init__(self):
        self.bot_constants = AppConstants()
        self.bot_variables = AppVariables()
        self.operations = Operations()

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

    def insert_strava_data(self, athlete_id, strava_data):
        database_connection = psycopg2.connect(self.bot_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.bot_constants.QUERY_UPDATE_STRAVA_DATA.format(strava_data=strava_data,
                                                                          athlete_id=athlete_id))
        cursor.close()
        database_connection.commit()
        database_connection.close()

    def process(self, athlete_id):
        athlete_token = self.get_athlete_token(athlete_id)
        if athlete_token:
            calculate_stats = CalculateStats(athlete_token)
            calculated_stats = calculate_stats.calculate()
            calculated_stats = json.dumps(calculated_stats)
            self.insert_strava_data(athlete_id, calculated_stats)

    def get_bikes(self, athlete_id):
        athlete_token = self.get_athlete_token(athlete_id)
        calculate_stats = CalculateStats(athlete_token)
        bikes = calculate_stats.get_bikes()
        return bikes
