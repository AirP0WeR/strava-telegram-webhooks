#  -*- encoding: utf-8 -*-

from iron_cache import IronCache

from app.common.constants_and_variables import AppVariables


class IronCacheClient:

    def __init__(self):
        self.bot_variables = AppVariables()

    def cache(self):
        cache = IronCache(project_id=self.bot_variables.iron_cache_project_id,
                          token=self.bot_variables.iron_cache_token)
        return cache
