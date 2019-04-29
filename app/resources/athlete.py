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

    def update_token_in_challenges(self, access_info, athlete_id):
        query = self.app_constants.QUERY_UPDATE_TOKEN_IN_CHALLENGES.format(
            access_token=self.aes_cipher.encrypt(access_info['access_token']),
            refresh_token=self.aes_cipher.encrypt(access_info['refresh_token']),
            expires_at=access_info['expires_at'],
            athlete_id=athlete_id
        )
        logging.info("Updating token details for {athlete_id} in challenges..".format(athlete_id=athlete_id))
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

    def get_athlete_details_by_telegram_username(self, telegram_username):
        athlete_details = dict()
        query = self.app_constants.QUERY_FETCH_ATHLETE_DETAILS_BY_TELEGRAM_USERNAME.format(
            telegram_username=telegram_username)
        logging.info("Getting athlete details for {telegram_username}".format(telegram_username=telegram_username))
        result = self.database_resource.read_operation(query)
        if result:
            athlete_details['athlete_id'] = result[0]
            athlete_details['telegram_username'] = telegram_username
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
                self.update_token(access_info, athlete_details['athlete_id'])
                athlete_details['athlete_token'] = access_info['access_token']
                athlete_details['refresh_token'] = access_info['refresh_token']
                athlete_details['expires_at'] = access_info['expires_at']

        return athlete_details if athlete_details != [] else False

    def get_athlete_details_in_challenges(self, athlete_id):
        athlete_details = dict()
        query = self.app_constants.QUERY_FETCH_ATHLETE_DETAILS_IN_CHALLENGES.format(athlete_id=athlete_id)
        logging.info("Getting athlete details for {athlete_id} in challenges".format(athlete_id=athlete_id))
        result = self.database_resource.read_operation(query)
        if result:
            athlete_details['athlete_id'] = athlete_id
            athlete_details['name'] = result[0]
            athlete_details['athlete_token'] = self.aes_cipher.decrypt(result[1])
            athlete_details['refresh_token'] = self.aes_cipher.decrypt(result[2])
            athlete_details['expires_at'] = result[3]
            athlete_details['even_challenges'] = result[4]
            athlete_details['even_challenges_data'] = result[5]
            athlete_details['odd_challenges'] = result[6]
            athlete_details['odd_challenges_data'] = result[7]
            athlete_details['bosch_even_challenges'] = result[4]
            athlete_details['bosch_even_challenges_data'] = result[5]
            athlete_details['bosch_odd_challenges'] = result[6]
            athlete_details['bosch_odd_challenges_data'] = result[7]

            if int(time.time()) > athlete_details['expires_at']:
                logging.info("Token has expired.")
                access_info = self.strava_resource.refresh_challenges_token(athlete_details['refresh_token'])
                self.update_token_in_challenges(access_info, athlete_id)
                athlete_details['athlete_token'] = access_info['access_token']
                athlete_details['refresh_token'] = access_info['refresh_token']
                athlete_details['expires_at'] = access_info['expires_at']

        return athlete_details if athlete_details != [] else False

    def get_athlete_id(self, telegram_username):
        athlete_id = False
        logging.info("Getting Athlete ID for: {telegram_username}".format(telegram_username=telegram_username))
        result = self.database_resource.read_operation(
            self.app_constants.QUERY_GET_ATHLETE_ID.format(telegram_username=telegram_username))
        if result:
            athlete_id = result[0]

        return athlete_id

    def get_stats(self, telegram_username):
        stats = False
        logging.info("Getting stats for: {telegram_username}".format(telegram_username=telegram_username))
        result = self.database_resource.read_operation(
            self.app_constants.QUERY_GET_STRAVA_DATA.format(telegram_username=telegram_username))
        if result:
            stats = result[0]

        return stats

    def enable_activity_summary(self, chat_id, athlete_id):
        enable = False
        logging.info("Enabling activity summary for {athlete_id} with chat id: {chat_id}".format(chat_id=chat_id,
                                                                                                 athlete_id=athlete_id))
        if self.database_resource.write_operation(
                self.app_constants.QUERY_ACTIVITY_SUMMARY_ENABLE.format(chat_id=chat_id, athlete_id=athlete_id)):
            enable = True

        return enable

    def disable_activity_summary(self, athlete_id):
        success = False
        logging.info("Disabling activity summary for: {athlete_id}".format(athlete_id=athlete_id))
        if self.database_resource.write_operation(
                self.app_constants.QUERY_ACTIVITY_SUMMARY_DISABLE.format(athlete_id=athlete_id)):
            success = True

        return success

    def disable_auto_update_indoor_ride(self, athlete_id):
        success = False
        logging.info("Disabling auto update indoor ride for: {athlete_id}".format(athlete_id=athlete_id))
        if self.database_resource.write_operation(
                self.app_constants.QUERY_UPDATE_INDOOR_RIDE_DISABLE.format(athlete_id=athlete_id)):
            success = True

        return success

    def update_chat_id(self, chat_id, athlete_id):
        success = False
        logging.info(
            "Updating chat id for {athlete_id} | Chat ID: {chat_id}".format(chat_id=chat_id, athlete_id=athlete_id))
        if self.database_resource.write_operation(
                self.app_constants.QUERY_UPDATE_CHAT_ID.format(chat_id=chat_id, athlete_id=athlete_id)):
            success = True

        return success

    def activate_deactivate_flag_athlete(self, operation, athlete_id):
        success = False
        if operation:
            logging.info("Activating athlete: {athlete_id}".format(athlete_id=athlete_id))
            query = self.app_constants.QUERY_ACTIVATE_ACTIVE_FLAG_ATHLETE.format(athlete_id=athlete_id)
        else:
            logging.info("Deactivating athlete: {athlete_id}".format(athlete_id=athlete_id))
            query = self.app_constants.QUERY_DEACTIVATE_ACTIVE_FLAG_ATHLETE.format(athlete_id=athlete_id)
        if self.database_resource.write_operation(query):
            success = True

        return success

    def deauthorise_from_challenges(self, athlete_id):
        success = False
        athlete_details = self.get_athlete_details_in_challenges(athlete_id)
        if self.strava_resource.deauthorise_athlete(athlete_details['athlete_token']):
            success = True
        else:
            logging.error("Failed to deauthorise {athlete_id}".format(athlete_id=athlete_id))

        return success
