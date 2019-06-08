#  -*- encoding: utf-8 -*-

import logging
import traceback

from app.clients.database import DatabaseClient
from app.common.constants_and_variables import AppVariables, AppConstants


class DatabaseResource:

    def __init__(self):
        self.app_variables = AppVariables()
        self.app_constants = AppConstants()
        self.database_client = DatabaseClient()

    def read_operation(self, query):
        result = list()
        database_connection = self.database_client.get_connection()
        cursor = database_connection.cursor()
        try:
            logging.info("Executing query with fetchone. Query: %s", query)
            cursor.execute(query)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            result = cursor.fetchone()
        finally:
            cursor.close()
            database_connection.close()
            logging.info("Result: %s", result)
            return result if result != {} else False

    def read_all_operation(self, query):
        result = list()
        database_connection = self.database_client.get_connection()
        cursor = database_connection.cursor()
        try:
            logging.info("Executing query with fetchall. Query: %s", query)
            cursor.execute(query)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            result = cursor.fetchall()
        finally:
            cursor.close()
            database_connection.close()
            logging.info("Result: %s", result)
            return result if result != {} else False

    def write_operation(self, query):
        result = False
        database_connection = self.database_client.get_connection()
        cursor = database_connection.cursor()
        try:
            logging.info("Executing write operation. Query: %s", query)
            cursor.execute(query)
            database_connection.commit()
        except Exception:
            logging.error(traceback.format_exc())
        else:
            result = True
        finally:
            cursor.close()
            database_connection.close()
            logging.info("Result: %s", result)
            return result
