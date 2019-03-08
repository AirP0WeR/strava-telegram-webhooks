#  -*- encoding: utf-8 -*-

import logging
import traceback

from app.clients.iron_cache import IronCacheClient


class IronCacheResource(object):

    def __init__(self):
        self.iron_cache_client = IronCacheClient().cache()

    def put_cache(self, cache, key, value):
        result = False
        try:
            logging.info(
                "Requesting put operation on cache. Cache: {cache} | Key: {key} | Value: {value}".format(cache=cache,
                                                                                                         key=key,
                                                                                                         value=value))
            self.iron_cache_client.put(cache=cache, key=key, value=value)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            result = True

        logging.info("Result: {result}".format(result=result))
        return result
