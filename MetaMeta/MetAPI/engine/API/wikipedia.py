import wikipedia
import time

from MetAPI.engine.API.webAPI import WebAPI

# don't use this crap, it doesn't work

class Wikipedia(WebAPI):


    def __init__(self) -> None:
        super().__init__()


    async def search(self, user_request, nb_result = 5):
        response_time = time.time()
        first_articles = wikipedia.search(user_request)
        response_time = time.time() - response_time
        return ([wikipedia.page(article) for article in first_articles], response_time)