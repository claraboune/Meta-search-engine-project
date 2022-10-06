import requests
from lxml import html
import time

from MetAPI.engine.abstractEngine import AbstractEngine


class GoogleScholar(AbstractEngine):

    def __init__(self) -> None:
        # l'URL ici est déjà une recherche, il faudra la minimiser
        self.URL = "https://scholar.google.com/scholar?hl=fr&as_sdt=0%2C5&q="
        self.name = "GoogleScholar"
        pass

    def extract(self, s):
        s = s.text_content()
        if not("Cité" in s):
            return 0
        s = s[s.index("Cité") + 5:]
        quotes = s.split()[0]
        return (quotes.isnumeric() and int(quotes))*1

    def key(self, x):
        return x["quotes"]

    async def search(self, user_request='', nb_result=5):
        R = []
        response_time = time.time()
        url = self.URL + user_request.replace(" ", '+')
        page = requests.get(url)
        tree = html.fromstring(page.content)
        list_results = tree.xpath('//div[@class="gs_ri"]')
        key_list = tree.xpath('//div[@class="gs_fl"]')
        for i in range(min(len(list_results), nb_result)):
            R.append({"quotes": self.extract(
                key_list[i]), "text": list_results[i].text_content()})
        response_time = time.time() - response_time
        return (R, response_time)
