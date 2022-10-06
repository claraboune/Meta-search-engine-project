from dotenv import load_dotenv
import os
import time

from engine.API.webAPI import WebAPI

# test par injection de dépendance
# voir wikipedia : inversion de controle (POO)
import twitter

class twitter:
    search()

class Twitter(WebAPI, engine):

    def __init__(self) -> None:
        self.bearer_token = load_dotenv(override=True)
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.endpoint_url = "https://api.twitter.com/1.1/search/tweets.json"
        
        if engine:
            self.engine = engine
        else:
            self.engine = twitter()

    def key(self, x):
        return x["fav"] + x["retweet"]

    async def search(self, user_request: str, nb_result=5):
        """
        q la recherche en elle-même
        count le nombre de tweet désiré

        more info @ : https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets
        """
        params = {'q': user_request,
                  'tweet.fields': 'author_id', 'count': nb_result}
        response_time = time.time()
        json_response = self.connect_to_endpoint(self.endpoint_url, params)
        # json_response is type dict
        response_time = time.time() - response_time
        response = []
        for status in json_response["statuses"]:
            response.append({"text": status["text"],
                            "retweet": status["retweet_count"],
                             "fav": status["favorite_count"]})
            response[-1]["user"] = status["user"]["name"]
            response[-1]["user_at"] = status["user"]["screen_name"]
            response[-1]["followers"] = status["user"]["followers_count"]
        return (response, response_time)

    def bearer_oauth(self, r):
        """
        'Method required by bearer token authentication.'
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r
