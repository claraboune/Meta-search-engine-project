import requests
from MetAPI.engine.abstractEngine import AbstractEngine


class WebAPI(AbstractEngine):
    """
    A class used to represent the search engines API

    Methods
    -------
    connect_to_endpoint(url, params)
        Connects to the API's endpoint.
    search(user_request)
        Does an asynchronous search on all the search
        engines' API.
    """

    def __init__(self) -> None:
        super().__init__()

    def connect_to_endpoint(self, url, params):
        """Connects to the API's endpoint.

        Parameters
        ----------
        url : str
            The API's url.
        params : tuple
            The parameters needed to complete the url (e.g. number of tweets)
        """

        response = requests.get(url, auth=self.bearer_oauth, params=params)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    async def search(self, user_request, nb_result=5):
        """Does an asynchronous search on all the search
        engines' API.

        Parameters
        ----------
        user_request : str
            The request the user types on the command bar.
        """

        return super().search(user_request)
