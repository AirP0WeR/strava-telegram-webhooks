#  -*- encoding: utf-8 -*-

import logging
import time

from app.common.aes_cipher import AESCipher
from app.common.constants_and_variables import AppVariables, AppConstants
from app.resources.database import DatabaseResource
from app.resources.strava import StravaResource


class AthleteResource(object):

    def __init__(self):
        self.app_variables = AppVariables()
        self.app_constants = AppConstants()
        self.database_resource = DatabaseResource()
        self.aes_cipher = AESCipher(self.app_variables.crypt_key_length, self.app_variables.crypt_key)
        self.strava_resource = StravaResource()

    def exists(self, athlete_id):
        query = self.app_constants.QUERY_ATHLETE_EXISTS.format(athlete_id=athlete_id)
        count = self.database_resource.read_operation(query)

        return True if count[0] > 0 else False

    def update_token(self, access_info, athlete_id):
        query = self.app_constants.QUERY_UPDATE_TOKEN.format(
            access_token=self.aes_cipher.encrypt(access_info['access_token']),
            refresh_token=self.aes_cipher.encrypt(access_info['refresh_token']),
            expires_at=access_info['expires_at'],
            athlete_id=athlete_id
        )
        logging.info("Updating token details for {athlete_id}..".format(athlete_id=athlete_id))
        return self.database_resource.write_operation(query)

    def get_athlete_details(self, athlete_id):
        athlete_details = dict()
        query = self.app_constants.QUERY_FETCH_ATHLETE_DETAILS.format(athlete_id=athlete_id)
        logging.info("Getting athlete details for {athlete_id}".format(athlete_id=athlete_id))
        result = self.database_resource.read_operation(query)
        if result:
            athlete_details['athlete_id'] = athlete_id
            athlete_details['telegram_username'] = result[0]
            athlete_details['name'] = result[1]
            athlete_details['athlete_token'] = self.aes_cipher.decrypt(result[2])
            athlete_details['refresh_token'] = self.aes_cipher.decrypt(result[3])
            athlete_details['expires_at'] = result[4]
            athlete_details['strava_data'] = result[5]
            athlete_details['update_indoor_ride'] = result[6]
            athlete_details['update_indoor_ride_data'] = result[7]
            athlete_details['chat_id'] = result[8]
            athlete_details['enable_activity_summary'] = result[9]

            if int(time.time()) > athlete_details['expires_at']:
                logging.info("Token has expired.")
                access_info = self.strava_resource.refresh_token(athlete_details['refresh_token'])
                self.update_token(access_info, athlete_id)
                athlete_details['athlete_token'] = access_info['access_token']
                athlete_details['refresh_token'] = access_info['refresh_token']
                athlete_details['expires_at'] = access_info['expires_at']

        return athlete_details if athlete_details != [] else False

    def get_token(self, athlete_id):
        access_token = False
        logging.info("Getting token for athlete: {athlete_id}".format(athlete_id=athlete_id))
        result = self.database_resource.read_operation(
            self.app_constants.QUERY_FETCH_TOKEN.format(athlete_id=athlete_id))
        if result:
            access_token = self.aes_cipher.decrypt(result[0])
            refresh_token = self.aes_cipher.decrypt(result[1])
            expires_at = result[2]

            if int(time.time()) > expires_at:
                logging.info("Token has expired.")
                access_info = self.strava_resource.refresh_token(refresh_token)
                access_token = access_info['access_token']
                self.update_token(access_info, athlete_id)

        return access_token
