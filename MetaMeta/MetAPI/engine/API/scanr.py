from pprint import pprint
import requests
from MetAPI.engine.API.webAPI import WebAPI
import logging
import time

class ScanR(WebAPI):

    def __init__(self) -> None:
        self.endpoint_url = (
            "https://scanr-api.enseignementsup-recherche.gouv.fr/"
            "api/v2/publications/search")
        self.params = {
                        "pageSize": 10,
                        "query": None
                        }
    
    async def search(self, user_request: str, nb_result = 5) -> dict:
        """[effectue une recherche sur l'API ScanR]

        Args:
            user_request (str): [input de l'utilisateur] -> si l'utilisateur
            tape "john doe", on envoie une requête "john doe" à scan R

        Returns:
            dict: [résultats de scanR sous forme d'un dict de dict]
        """
        response_time = time.time()
        self.params["query"] = user_request
        json_response = requests.post(
            self.endpoint_url,
            json=self.params
        )
        json_response = json_response.json()

        logging.debug(f"Réponse brute : {json_response, }")

        n = min(self.params["pageSize"], len(json_response['results']))

        for k in range(n):
            logging.debug(f"\n\njson_response['results'][k]['value'] "
                f"({k})\n\n {json_response['results'][k]['value']}"
            )
            logging.debug(f"\n\nHIGHLIGHTS ({k})\n\n "
                f"{json_response['results'][k]['highlights']}")

        self.res =[ {
        "title": self.extract_title(json_response, index= k),
        "authors": [author['fullName'] for author in 
            json_response['results'][k]["value"]["authors"]],
        "domains": self.get_domain(json_response['results'], k),
        "source": self.source_or_type(json_response, index = k),
        "id": json_response['results'][k]["value"]["id"]
        } for k in range(n) ]
        response_time = time.time() - response_time
        return (self.res, response_time)
    
    def try_keyword(self, dict, key_list):
        for keyword in key_list :
            try :
                return dict[keyword]
            except :
                pass
        return

    def get_domain(self, dict, index):
        if "domains" in dict[index]["value"]:
            domains_res = [self.try_keyword(domain["label"], ["fr", "en", "default"]) for domain in dict[index]["value"]["domains"]]
        else :
            domains_res = ["None"]

        return domains_res

    def format_response(self) -> dict:
        """[renvoie la réponse sous forme html]

        Returns:
            dict: [dictionnaire des réponses formatté en strings html]
        """
        formatted_res = {
        "title":  self.highlight_strong_html("".join(self.res["title"])), 
        "authors": " | ".join(self.res["authors"]),
        "domains": " | ".join(self.res["domains"]),
        "source": self.res["source"],
        "id": self.res["id"]
        }    
        return formatted_res
    
    @staticmethod
    def highlight_strong_html(str : str) -> str:
        """[rajoute des balises de highlight à chaque balise strong]

        Args:
            str (str): [html string]

        Returns:
            str: [html string]
        """
        return str.replace(
            "<strong>", "<aaa fg='black' bg='ansiyellow'> <strong>"
            ).replace("</strong>", "</strong></aaa> ")
        
    @staticmethod
    def source_or_type(json_response, index: int):
        """[gestion de collision : renvoie le type de papier si aucune 
        source n'est disponible]

        Args:
            json_response ([type]): [description]
            index (int): [description]

        Returns:
            [type]: [description]
        """
        if "source" in json_response['results'][index]["value"]:
            return json_response['results'][index]["value"]["source"]["title"]
        else:
            return json_response['results'][index]["value"]['productionType']
    
    @staticmethod
    def extract_dict(dict_list: list, key: str, value: str) -> dict:
        """[renvoie le premier dict qui contient une valeur partiuclière pour 
        une clé particulière parmis une liste de dict]

        Args:
            dict_list (list):[liste des dict d ou on extrait le dict recherché]
            key (str):[nom de la clé que l'on recherche]
            value (str):[valeur de la clé que l'on souhaite]

        Returns:
            dict: [premier dict contenant la clé recherchée]
        """
        # on parcourt la liste des dict
        for dict in dict_list:
            logging.debug(
                f"\n\nDICT : {dict}\n\ntest {key} in dict : {key in dict}"
                )
            # si la clé est dans le dict
            if key in dict:
                logging.debug(f"\n{key} is in dict ! looking if dict[{key}] "
                f"== {value} : {dict[key] == value}\n"
                )
                # est elle égale à la valeur souhaitée ?
                if value in dict[key]:
                    logging.debug(f"returning : {dict}")
                    return dict
        # si on n'a rien trouvé ( aucun match ) on retourne une None
        return dict_list[0]
        
    
    def extract_title(self, json_response, index):
        """[gestion de collision : si le papier ne possède pas de titre, 
        renvoie sa description à la place]

        Args:
            json_response ([type]): [raw response from ScanR]
            index ([type]): [index du papier dans la recherche]

        Returns:
            [type]: [description]
        """
        extract_dicted=self.extract_dict(
            json_response['results'][index]["highlights"], key="type",
            value="title"
            )
        if extract_dicted is None:
            extract_dicted=self.extract_dict(
                json_response['results'][index]["highlights"],
                key="type", value="summary" 
                )
            if extract_dicted is None :
                extract_dicted=self.extract_dict(
                json_response['results'][index]["highlights"],
                key="type", value="label" 
                )   
        return extract_dicted["value"] 
        

if __name__ == "__main__":
    s = ScanR()
    res = s.search("localement\ compact")
    pprint(res)