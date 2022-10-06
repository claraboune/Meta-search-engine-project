import requests
from bs4 import BeautifulSoup
import time

from MetAPI.engine.abstractEngine import AbstractEngine


class CNRTL(AbstractEngine):
    def __init__(self):
        pass

    async def search(self, user_request, nb_result=5):
        response_time = time.time()
        definition = dict()
        sentence = user_request.split()
        sentence.sort(key=lambda word: len(word), reverse=True)
        len_sentence = len(sentence)
        word_index = 0
        while len(definition) == 0 and word_index < len_sentence:
            URL = "https://www.cnrtl.fr/definition/" + str(
                sentence[word_index]
                )
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
            # chooses a specific element thanks to its id
            content = soup.find(id="contentbox")
            # looks for all the yellow highlighted definitions
            yellow_highlights = content.find_all(
                "span", class_="tlf_cdefinition"
                )
            # creates a list with each of the definitions
            def_list = [definition.text.strip()
                        for definition in yellow_highlights]
            definition = {sentence[word_index]: def_list}
            word_index += 1
        response_time = time.time() - response_time
        return (definition, response_time)
