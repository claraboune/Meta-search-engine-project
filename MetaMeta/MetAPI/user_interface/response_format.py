from prompt_toolkit import print_formatted_text, HTML
import pprint

def highlight(str, fg_color, bg_color):
    return f"<aaa fg='{fg_color}' bg='{bg_color}'> <strong>" + str + "</strong> </aaa>"

def html_escape(text: object) -> str:
    # The string interpolation functions also take integers and other types.
    # Convert to string first.
    if not isinstance(text, str):
        text = "{}".format(text)

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def Giphy_format(response):
    nb_link = len(response)
    if nb_link > 0 :
        
        engine_html_str = f"\n\n<strong>ENOOOOORME</strong> on a trouvé <aaa fg='black' bg='ansiyellow'> <strong>{nb_link}</strong> </aaa> résultats :\n"
        for k in range(nb_link) :
            number_html_str = "\t" + highlight(str(k+1), "black", "ansigreen")
            engine_html_str += number_html_str
            link_html_str = "\t" + "<u><i><aaa fg='ansiblue'>" + response[k] + "</aaa></i></u>"
            engine_html_str += link_html_str
            engine_html_str += "\n"
    else :
        engine_html_str = "OH NON ! on n'a <aaa fg='black' bg='ansired'> <strong>rien</strong> </aaa> trouvé :("
    return engine_html_str

def Statistics_format(response):
    L = [[i, j] for i, j in response.items()]
    L.sort(key = lambda x : x[1], reverse = True)
    m = max([len(item[0]) for item in L])
    L = [item[0].rjust(m + 1) + 
        ' : ' + highlight(str(item[1]), "black", "blue") for item in L]
    stat_html = '\n'.join(L)
    # print(stat_html)
    print_formatted_text(HTML(stat_html))

def HealthCheck_format(response):
    response = response.text.replace('\\n', '\n').replace('\\t', '\t')
    L = response.split('\n')
    L = [item.center(80, '*') for item in L]
    response = '\n'.join(L)
    HTMLresponse = highlight(response, "black", "ansiyellow")

    print_formatted_text(HTML(HTMLresponse))


def CNRTL_format(response):
    
    cnrtl_html = ""
    
    cnrtl_word = html_escape(list(response.keys())[0])
    cnrtl_html = highlight(cnrtl_word, "black", "pink") + "\n"*2

    for definition in response[cnrtl_word] :
        definition_html = highlight(html_escape(definition), "black", "yellow")
        cnrtl_html += definition_html + "\n"*2
        #cnrtl_html += cnrtl_definition + "\n"
    cnrtl_html
    
    return cnrtl_html

def Twitter_format(response):
    
    tweeter_html = ""
    
    for tweet in response :
        tweet["user_at"] = html_escape(tweet["user_at"])
        tweet["text"] = html_escape(tweet["text"])
        tweet_author = highlight("@" + tweet["user_at"], "black", "ansiyellow") + highlight(str(tweet["followers"]) + " followers", "black", "ansipurple")
        tweet_html = highlight(tweet["text"], "black", "ansiblue")
        tweet_stats = highlight( "fav : " + str(tweet["fav"]), "black", "ansired") + "\t" + highlight("rt : " + str(tweet["retweet"]), "black", "ansigreen")
        
        tweeter_html += tweet_author + "\n"
        tweeter_html += tweet_html + "\n"
        tweeter_html += tweet_stats + "\n\n"
    
    
    return tweeter_html

def search_metadata_format(reponse):
    return ""

def GoogleScholar_format(response):
    final_html_str = ""
    for k in range(len(response)) :
        response[k]["text"] = html_escape(response[k]["text"])
        res_nb = highlight(f"RESULTAT n°{k+1} :", "black", "ansiyellow")
        text_html = highlight("Description :", "black", "ansigreen") + "\t" + response[k]["text"]
        quotes_html = highlight("Nombre de citations : ", "black", "ansigreen") + "\t" + str(response[k]["quotes"])
        final_html_str += res_nb + "\n"
        final_html_str += text_html +"\n"
        final_html_str += quotes_html +"\n\n"
    
    return final_html_str


def ScanR_format(response):
    return ""

def format_engine_reponse(engine, response):
    html_engine_str  = globals()[engine + "_format"](response)
    return html_engine_str



def format_result(response: dict, show_raw = False, show_formatted = True):
    if show_raw:
        pprint.pprint(response)
    
    if show_formatted:
        final_html_str = ""
        response.pop("search_metadata")
        for engine_name in response:
            
            engine_response = response[engine_name]
            
            engine_name_html_str = highlight(f"( | {engine_name} | )", "black", "pink") 
            engine_html_str = format_engine_reponse(engine_name, engine_response)
            
            final_html_str += engine_name_html_str + "\n"
            final_html_str += engine_html_str
            final_html_str += "\n\n"
        
        print_formatted_text(HTML(final_html_str))
