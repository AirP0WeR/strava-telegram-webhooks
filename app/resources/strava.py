#  -*- encoding: utf-8 -*-

import logging
import traceback

import requests

from app.clients.strava import StravaClient
from app.common.constants_and_variables import AppVariables, AppConstants


class StravaResource:

    def __init__(self):
        self.app_variables = AppVariables()
        self.app_constants = AppConstants()
        self.strava_client = StravaClient()

    def token_exchange(self, code):
        access_info = dict()
        try:
            logging.info("Exchanging token..")
            response = requests.post(self.app_constants.API_TOKEN_EXCHANGE, data={
                'client_id': int(self.app_variables.client_id),
                'client_secret': self.app_variables.client_secret,
                'code': code,
                'grant_type': 'authorization_code'
            }).json()
        except Exception:
            logging.error(traceback.format_exc())
        else:
            access_info['athlete_id'] = response['athlete']['id']
            access_info['name'] = "{first_name} {last_name}".format(first_name=response['athlete']['firstname'],
                                                                    last_name=response['athlete']['lastname'])
            access_info['access_token'] = response['access_token']
            access_info['refresh_token'] = response['refresh_token']
            access_info['expires_at'] = response['expires_at']

        logging.info("Result: %s", access_info)
        return access_info if access_info != [] else False

    def token_exchange_for_challenges(self, code):
        access_info = dict()
        try:
            logging.info("Exchanging token..")
            response = requests.post(self.app_constants.API_TOKEN_EXCHANGE, data={
                'client_id': int(self.app_variables.challenges_client_id),
                'client_secret': self.app_variables.challenges_client_secret,
                'code': code,
                'grant_type': 'authorization_code'
            }).json()
        except Exception:
            logging.error(traceback.format_exc())
        else:
            access_info['athlete_id'] = response['athlete']['id']
            access_info['name'] = "{first_name} {last_name}".format(first_name=response['athlete']['firstname'],
                                                                    last_name=response['athlete']['lastname'])
            access_info['access_token'] = response['access_token']
            access_info['refresh_token'] = response['refresh_token']
            access_info['expires_at'] = response['expires_at']

        logging.info("Result: %s", access_info)
        return access_info if access_info != [] else False

    def refresh_token(self, refresh_token):
        access_info = dict()
        try:
            logging.info("Refreshing token..")
            response = requests.post(self.app_constants.API_TOKEN_EXCHANGE, data={
                'client_id': int(self.app_variables.client_id),
                'client_secret': self.app_variables.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }).json()
        except Exception:
            logging.error(traceback.format_exc())
        else:
            access_info['access_token'] = response['access_token']
            access_info['refresh_token'] = response['refresh_token']
            access_info['expires_at'] = response['expires_at']

        logging.info("Result: %s", access_info)
        return access_info if access_info != [] else False

    def refresh_challenges_token(self, refresh_token):
        access_info = dict()
        try:
            logging.info("Refreshing token..")
            response = requests.post(self.app_constants.API_TOKEN_EXCHANGE, data={
                'client_id': int(self.app_variables.challenges_client_id),
                'client_secret': self.app_variables.challenges_client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }).json()
        except Exception:
            logging.error(traceback.format_exc())
        else:
            access_info['access_token'] = response['access_token']
            access_info['refresh_token'] = response['refresh_token']
            access_info['expires_at'] = response['expires_at']

        logging.info("Result: %s", access_info)
        return access_info if access_info != [] else False

    def update_strava_activity(self, token, activity_id, name, gear_id):
        strava_client = self.strava_client.get_client(token)
        result = False
        try:
            logging.info("Updating activity: Activity ID: %s | Name: %s | Gear ID: %s", activity_id, name, gear_id)
            strava_client.update_activity(activity_id=activity_id, name=name, gear_id=gear_id)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            result = True

        logging.info("Result: %s", result)
        return result

    def get_gear_name(self, token, gear_id):
        strava_client = self.strava_client.get_client(token)
        gear_name = False
        try:
            logging.info("Getting gear name for %s", gear_id)
            result = strava_client.get_gear(gear_id=gear_id)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            gear_name = result.name

        logging.info("Gear name: %s", gear_name)
        return gear_name

    def get_bikes_list(self, token):
        strava_client = self.strava_client.get_client(token)
        athlete = strava_client.get_athlete()
        bikes = dict()
        count = 1
        for bike in athlete.bikes:
            bikes.update({count: {'bike_name': bike.name, 'bike_id': bike.id}})
            count += 1

        return bikes

    def get_strava_activity(self, token, activity_id):
        strava_client = self.strava_client.get_client(token)
        activity = False
        try:
            logging.info("Getting activity %s..", activity_id)
            result = strava_client.get_activity(activity_id)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            logging.info("Success.")
            activity = result

        return activity

    def get_athlete_info(self, token):
        strava_client = self.strava_client.get_client(token)
        athlete = False
        try:
            logging.info("Getting athlete info..")
            result = strava_client.get_athlete()
        except Exception:
            logging.error(traceback.format_exc())
        else:
            logging.info("Success.")
            athlete = result

        return athlete

    def get_strava_activities_after_date(self, token, after_date):
        strava_client = self.strava_client.get_client(token)
        activity = False
        try:
            logging.info("Getting activities after %s..", after_date)
            result = strava_client.get_activities(after=after_date)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            logging.info("Success.")
            activity = result

        return activity

    def get_strava_activities_after_date_before_date(self, token, after_date, before_date):
        strava_client = self.strava_client.get_client(token)
        activity = False
        try:
            logging.info("Getting activities after %s and before %s..", after_date, before_date)
            result = strava_client.get_activities(after=after_date, before=before_date)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            logging.info("Success.")
            activity = result

        return activity

    def deauthorise_athlete(self, token):
        strava_client = self.strava_client.get_client(token)
        success = False
        try:
            logging.info("Deauthorising..")
            strava_client.deauthorize()
        except Exception:
            logging.error(traceback.format_exc())
        else:
            logging.info("Success.")
            success = True

        return success
