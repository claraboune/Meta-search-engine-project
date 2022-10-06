import platform
import logging
import MetAPI.user_interface.response_format as response_format
import json


"""
Couleur
"""
from colorama import Fore


"""
CLI Libraries
"""
import prompt_toolkit
# prompt_toolkit . print_formatted_text, HTML
from inquirer2 import prompt

# cool title
from pyfiglet import Figlet

import pprint

"""
CLEAR FUNCTION
"""
import os


def clear():
    running_system = platform.system()
    Posix_Systems = ["Linux",
                     "Darwin"   # MAC OS
                     ]
    if running_system in Posix_Systems:
        os.system('clear')
    elif running_system == "Windows":
        os.system('cls')

    return


"""
REQUETES
"""

import requests
import json
headers = {'accept': 'application/json'}
API_URL = 'http://127.0.0.1:8000/'


"""
STYLE
"""

red_color = "#E91E63"
blue_color = "#2196f3"
orange_color = "#ff8700"
cyan_color = "#00ffd7"

style = prompt_toolkit.styles.Style([
    ('separator',    red_color),
    ('questionmark', red_color),
    ('focus',        blue_color),
    ('checked',      blue_color),
    ('pointer',      orange_color),
    ('instruction',  orange_color),
    ('answer',       cyan_color),
    ('question',     blue_color),
])


# ! compléter la liste de ce qu'on peut configurer
Config_List = ["engines in use", "cross-engine sort", "purge cache"]
Stats_List = ["top queries", "raw statistics in file"]
AllEngines = [{'name' : 'Twitter'}, 
                {'name' : 'ScanR'},
                {'name' : 'GoogleScholar'},
                {'name' : 'Giphy'},
                {'name' : 'CNRTL'},
                {'name' : 'purge cache'}]

show_raw_bool = False
show_formatted_bool = True


def menu():
    questions = [

        {
            'type': 'list',
            'name': 'app_choice',
            'message': 'What do you want to do ?',
            'choices': ['search', 'statistics', 'health check', 'configure', 'quit']
        },

        # >>>> Adapter List <<<<


        #   Search

        {
            'type': 'input',
            'name': 'search_type',
            'message': 'Please type what you want to search : ',
            # 'default': cartes_dispo[1],
            'when': lambda answers : answers['app_choice'] == 'search'
        },


        #   Config
        {
            'type': 'list',
            'name': 'choose_config',
            'message': 'What do you want to config ?',
            'choices': Config_List,
            'when': lambda answers : answers['app_choice'] == 'configure'
        },

        #   Statistics
        {
            'type' : 'list',
            'name' : 'get_some_statistics',
            'message' : 'what type of statistics do you want ?',
            'choices' : Stats_List,
            'when' : lambda answers : answers['app_choice'] == 'statistics'
        },

        #   How many queries ?
        {
            'type' : 'input',
            'name' : 'top_queries_number',
            'message' : 'Please specify the numbers of top queries you want : ',
            'when' : lambda answers : answers['app_choice'] == 'statistics' and 
                    answers['get_some_statistics'] == 'top queries'
        },

        #   Engines in use
        {
            'type' : 'checkbox',
            'name' : 'choose_engines',
            'message' : 'select wanted engines',
            'choices' : AllEngines,
            'when' : lambda answer : answer['app_choice'] == 'configure' and
                    answer['choose_config'] == 'engines in use',
            'validate': lambda answer: 'You must choose at least one topping.' \
            if len(answer) == 0 else True
        },

        # QUIT confirm
        {
            'type': 'confirm',
            'name': 'quit_confirm',
            'message': 'Do you want to Exit ?',
            'default': False,
            'when': lambda answers: answers['app_choice'] == 'quit'
        }

    ]
    answers = prompt.prompt(questions, style=style)
    return answers


def render_title():
    f = Figlet(font='slant')
    print(f.renderText('META META'))
    print(Fore.CYAN + "Le moteur qui te renvoie ce que dit l'internet, et ce que disent les experts !\n\n " + Fore.WHITE)
    print("---   " + Fore.YELLOW + "Github/allemand-instable" +
          Fore.WHITE + "   ---\n\n\n")


def action():
    logging.debug(f"running menu's action function")
    """exécute les actions demandées par l'utilisateur

    Returns:
        bool: retourne si le menu doit être ré-affiché après l'action effectuée
    """
    clear()
    render_title()

    # affiche le menu et retourne les résultats
    answer = menu()
    logging.debug(f"user interface choices : {answer}")

    if answer['app_choice'] == 'search':
        
        # définition des paramètres de la requête
        params = (
            ('data',answer['search_type']),
        )
        
        # obtention des résultats de l'API
        response = requests.get(API_URL + 'searches', params=params)
        
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        else:
            # print(Fore.CYAN + "RAW JSON : " + Fore.WHITE)
            # pprint.pprint(json.dumps(response.json(), indent=4, sort_keys=True, ensure_ascii=False))

            # print(Fore.CYAN + "Formatted Response : " + Fore.WHITE)
            
            if len(response.json()) != 0:
                response_format.format_result(
                    response.json(),
                    show_raw= show_raw_bool,
                    show_formatted= show_formatted_bool
                    )
                
                input("press ENTER to continue")
            
    elif answer['app_choice'] == "statistics" and answer["get_some_statistics"] == "raw statistics in file":
        params = (
            ('raw', '1'),
        )

        response = requests.get(API_URL + 'statistics', params=params)
        with open('raw_statistics.json', 'w') as outfile:
            json.dump(response.json(), outfile, indent=4)

    elif answer['app_choice'] == "statistics":

        params = (
            ('top_query', answer['top_queries_number']),
        )

        response = requests.get(API_URL + 'statistics', params=params)
        # ça serait cool ici de faire un response format et de trier ces réponses
        response_format.Statistics_format(response.json())
        input("press ENTER to continue")

    

    elif answer['app_choice'] == "health check":
        response = requests.get(API_URL + 'healthcheck')
        response_format.HealthCheck_format(response)
        input("press ENTER to continue")

    elif answer['app_choice'] == "configure" and answer['choose_config'] == 'engines in use':
        purge = "purge cache" in answer['choose_engines']
        index = purge and (answer['choose_engines'].index("purge cache"))
        engines = answer['choose_engines']
        if purge:
            engines.pop(index)
        params = (
                ('engines', ' '.join(engines)),
                ('purge', purge*1),
                )

        response = requests.put(API_URL + 'config', params=params)
        input("press ENTER to continue")

    elif answer['app_choice'] == "configure" and answer['choose_config'] == 'purge cache':
        params = (
                ('purge', '1'),
                )
        response = requests.put(API_URL + 'config', params=params)


    elif answer['app_choice'] == "configure" and answer['choose_config'] == 'cross-engine sort':
        headers = {'accept': 'application/json'}
        data = {'merge' : False, 
                'engines' : {'expert' : "GoogleScholar Twitter"}}

        response = requests.post(API_URL + "config/cross_engine", headers=headers, json=data)
        input("CURRENTLY NOT SUPPORTED \n press ENTER to continue")
        

    elif answer['app_choice'] == 'quit' and answer["quit_confirm"] == True:
        clear()
        return False

    # si l'utilisateur ne veut pas
    return True


def run():
    """
    continue la boucle
    """
    running = True
    while running:
        logging.debug("running is set to True, running action loop...")
        running = action()
        # ! replacer par un log

    return


def main():
    run()
    return



dico_test = {
   "Giphy" : [
      "https://giphy.com/gifs/mic-work-robots-jobs-12qq4Em3MVuwJW",
      "https://giphy.com/gifs/spongebob-season-4-spongebob-squarepants-l1KtYG8BndKBmWrM4",
      "https://giphy.com/gifs/SandiaLabs-robot-robotics-1lxryzbQaqo49cKhCw",
      "https://giphy.com/gifs/food-hungry-future-1vZfV4JewI8vhwLHcd",
      "https://giphy.com/gifs/SafranGroup-robot-future-innovation-r3oOElXxOl0mVpoKzg"
   ],
   "CNRTL" : {
      "automate" : [
         "Appareil renfermant divers dispositifs mécaniques ou électriques qui lui permettent d'exécuter un programme déterminé d'opérations :",
         "Machine qui reproduit le mouvement, les attitudes d'un être vivant :",
         "Personne qui agit mécaniquement, soit d'une manière inconsciente, soit sous l'impulsion d'une volonté extérieure :",
         "Qui a un comportement d'automate :"
      ]
   },
   "Twitter" : [
      {
         "user" : "Karl G. Schneider",
         "text" : "Cancelling all running flows in Power Automate – 365 HQ https://t.co/yJv8G6gKUA",
         "retweet" : 0,
         "user_at" : "schneika",
         "followers" : 676,
         "fav" : 0
      },
      {
         "user_at" : "thatmariia",
         "retweet" : 0,
         "user" : "Mariia Turchina",
         "text" : "It's apparently a very long and mundane process to send rec letter requests from each program to 3-4 recommenders,… https://t.co/R72e7bFq6V",
         "followers" : 147,
         "fav" : 0
      },
      {
         "retweet" : 114,
         "user_at" : "crashyoudown",
         "user" : "Crashd⬡wn",
         "text" : "RT @chainlink: #Chainlink Keepers empowers developers and #DAOs to automatically trigger smart contract logic when predefined conditions oc…",
         "fav" : 0,
         "followers" : 278
      },
      {
         "fav" : 0,
         "followers" : 583,
         "text" : "Eliminate manual and repetitive tasks by automating the workflow. Take a look at how OfficeClip rules will automate… https://t.co/0jg1XT5jFy",
         "user" : "OfficeClip",
         "retweet" : 0,
         "user_at" : "OfficeClip"
      },
      {
         "text" : "RT @QRmt2: 最近RPAデビューして、Power automateを触ってるんだけど、少しずつ理解できてきた。単純な仕事はロボにさせるって世の中になってきてるんだなぁ。ロボを動かせるようにならないとロボに仕事奪われちゃうとは怖い世の中ですよ。",
         "user" : "Claudia Pinto",
         "retweet" : 3,
         "user_at" : "Claudia60061150",
         "followers" : 35,
         "fav" : 0
      }
   ],
   "search_metadata" : {
      "Giphy_response_time" : 0.0584273338317871,
      "Twitter_response_time" : 0.375669002532959,
      "GoogleScholar_response_time" : 0.337552070617676,
      "CNRTL_response_time" : 0.224110841751099
   },
   "GoogleScholar" : [
      {
         "quotes" : 50,
         "text" : "[HTML][HTML] Automate asocial et systèmes acentrésP Rosenstiehl, J Petitot - Communications, 1974 - persee.frIl serait simpliste de penser que les concepts hiérarchiques imposés par ceux qui ont l'exercice du pouvoir correspondent véritablement à la nature des choses. Les organismes biologiques, les «sociétés» animales comme on dit, les a hordes» humaines de toutes …Enregistrer Citer Cité 50 fois Autres articles Les 7 versions  "
      },
      {
         "quotes" : 61,
         "text" : "[LIVRE][B] Philosophie des milieux techniques: la matière, l'instrument, l'automateJC Beaune - 1998 - books.google.comIl est beaucoup question dans ce livre de techniques, de technologie, de machines, d'outils, d'objets conçus et fabriqués, d'artifices, d'automates. Autant d'optiques qui se recouvrent en partie mais laissent, à travers cette pluralité revendiquée, entrevoir un point commun: un …Enregistrer Citer Cité 61 fois Autres articles Les 3 versions  "
      },
      {
         "quotes" : 59,
         "text" : "[LIVRE][B] De l'Informatique: savoir vivre avec l'automateM Volle - 2006 - volle.com… En prenant en charge dans les usines puis dans les bureaux la part répétitive du travail, l’automate \na rompu le lien qui, dans l’économie mécanisée, reliait l’emploi à la production et avait, malgré \nles crises et les guerres, procuré un équilibre endogène. Le réseau lui a conféré l’ubiquité. Il a …Enregistrer Citer Cité 59 fois Autres articles Les 7 versions  Version HTML "
      },
      {
         "text" : "Automate des préfixes-suffixes associé à une substitution primitiveV Canterini, A Siegel - Journal de théorie des nombres de Bordeaux, 2001 - numdam.orgOn explicite une conjugaison en mesure entre le décalage sur le système dynamique associé à une substitution primitive et une transformation adique sur le support d'un sous-shift de type fini, à savoir l'ensemble des chemins d'un automate dit des préfixes-suffixes. En …Enregistrer Citer Cité 74 fois Autres articles Les 8 versions  Version HTML ",
         "quotes" : 74
      },
      {
         "text" : "Sur les mots synchronisants dans un automate finiJE Pin - Elektron. Informationsverarb. Kybernet., 1978 - hal.uca.frLet A be a finite automaton. We are concerned with the minimal length of the words that send all states to a unique state (synchronizing words). J. Cerný has conjectured that, if there exists a synchronizing word in A then there exists such a word with length?(n-1)^ 2 …Enregistrer Citer Cité 48 fois Autres articles Les 4 versions  En cache ",
         "quotes" : 48
      }
   ]
}


# Définie la main
if __name__ == "__main__":
    main()
