import urllib.parse
import urllib.request
import json
from MetAPI.engine.API.webAPI import WebAPI
from dotenv import load_dotenv
import os
import time


class Giphy(WebAPI):
    """
    A class used to get Giphs from GIPHY API.

    Methods
    -------
    asyn_def(user_request, nb_result=5)
        Returns the giphs' url.
    """

    def __init__(self):
        self.bearer_token = load_dotenv(override=True)
        self.bearer_token = os.getenv('giphy_key')

    async def search(self, user_request, nb_result=5):
        """Returns the giph's url.

        If the argument 'nb_result' isn't passed in, the default
        GIPHY number of results is used.

        Parameters
        ----------
        user_request : str
            The request the user types on the command bar.
        nb_result : int
            The number of giphs wanted as a result of the request
            (default is 5)
        """

        url = "http://api.giphy.com/v1/gifs/search?"
        params = urllib.parse.urlencode({
            "api_key": self.bearer_token,
            "q": user_request,
            "limit": str(nb_result)
        })
        joined_params = "".join(params)
        complete_url = "".join([url, joined_params])
        response_time = time.time()
        with urllib.request.urlopen(complete_url) as response:
            dictionnaries = json.loads(response.read())
        # on récupère uniquement l'url du GIF.
        gifs = []
        for dict in dictionnaries["data"]:
            gifs.append(dict["url"])
        response_time = time.time() - response_time
        return (gifs, response_time)
