import asyncio
import dotenv
import os
import json

import psycopg2

from MetAPI.engine.API.twitter import Twitter
from MetAPI.engine.web_scrapping.googleScholar import GoogleScholar
from MetAPI.engine.web_scrapping.CNRTL import CNRTL
from MetAPI.engine.API.scanr import ScanR
from MetAPI.engine.API.giphy import Giphy
# from engine.API.wikipedia import Wikipedia

from MetAPI.DAO.cache import Cache
from MetAPI.DAO.db_connection import DBConnection


class Process:

    def __init__(self) -> None:
        dotenv.load_dotenv(override=True)
        engineList = os.environ["ENGINE_LIST"]
        AllEngines = [Twitter(), GoogleScholar(), Giphy(), ScanR(), CNRTL()]
        self.engineList = [
            engine for engine in AllEngines
            if engine.__class__.__name__ in engineList]
        self.res = None

    async def makeSearch(self, user_request: str, nb_result):
        Results = dict()
        metadata = dict()
        Tasks = [asyncio.create_task(engine.search(
            user_request, nb_result)) for engine in self.engineList]
        res = await asyncio.gather(*Tasks)
        for engine, response in zip(self.engineList, res):
            Results[engine.__class__.__name__] = response[0]
            metadata[engine.__class__.__name__ +
                     "_response_time"] = response[1]
            Results["search_metadata"] = metadata
        self.res = Results
        return self.res

    def addCache(self, user_request, result):
        cache = Cache()
        report = cache.put(user_request, result)
        if report is not None:
            return report

    def checkCache(self, user_request, user_ip):
        cache = Cache()
        res = cache.get(user_request, user_ip)
        if isinstance(res, psycopg2.Error):
            print(res)
            return Exception(
                "database issue ; check with the person in charge"
                )
        if len(res) == 0:
            return None
        return res[0]['results']

    def sortTogether(self):
        """This method sort results between differents engines.
        Every engine needs a key method in order to be sorted.

        The function add the key in the results, concatenate and sort them
        then remove keys from the results

        every result is now a dictionnary with it's engine name as the only key

        Returns:
            dict: {topic_name : results}
        """
        dotenv.load_dotenv(override=True)
        params = json.loads(os.environ["CROSS_ENGINE_PARAMS"])
        if params['merge']:
            for topic_name, engines in params['engines'].items():
                topic = []
                engineName = engines.split()
                d = {engine.__class__.__name__:
                     engine for engine in self.engineList}
                for engine in engineName:
                    for item in self.res[engine]:
                        topic.append(
                            {engine: item, "key": d[engine].key(item)})
                    self.res.pop(engine)
                topic.sort(key=lambda x: x["key"], reverse=True)
                for item in topic:
                    item.pop("key")
                self.res[topic_name] = topic
        return self.res

    def purgeCache(self, date):
        Cache.purge(Cache(), date)

    def raw_stats(self):
        return Cache.send_raw_stats(Cache())

    def get_stats(self, top_query=10):
        All_queries = Cache.send_raw_stats(Cache())
        d = dict()
        for query in All_queries:
            d[query["params"]] = ((query["params"] in d)
                                  and (d[query["params"]])) + 1
        L = list(d.items())
        L.sort(reverse=True, key=lambda tup: tup[1])
        return dict(L[:top_query])

    def check_connection(self):
        with DBConnection().connection as connection:
            return connection.closed == 0
