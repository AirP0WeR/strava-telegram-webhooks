#  -*- encoding: utf-8 -*-

import psycopg2

from app.common.constants_and_variables import AppVariables


class DatabaseClient(object):
    def __init__(self):
        self.app_variables = AppVariables()

    def read_operation(self, query):
        database_connection = psycopg2.connect(self.app_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        database_connection.close()

        return result

    def read_all_operation(self, query):
        database_connection = psycopg2.connect(self.app_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        database_connection.close()

        return result

    def write_operation(self, query):
        database_connection = psycopg2.connect(self.app_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(query)
        cursor.close()
        database_connection.commit()
        database_connection.close()
