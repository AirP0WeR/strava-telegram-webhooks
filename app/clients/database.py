#  -*- encoding: utf-8 -*-

import psycopg2

from app.common.constants_and_variables import AppVariables


class DatabaseClient(object):

    def __init__(self):
        self.app_variables = AppVariables()

    def get_connection(self):
        return psycopg2.connect(self.app_variables.database_url, sslmode='require')
