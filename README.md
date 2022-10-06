MetaMeta
=====================

MetaMeta is a metasearch application. The program compares search results from different search engines. There are two main types of search engines:
    - scholar search engines (e.g. GoogleScholar)
    - social media search engines (e.g. Twitter)


On the server side
-------------------

## Installation

Install fastapi.

```bash
pip install fastapi
```

Install the ASGI server uvicorn.

```bash
pip install "uvicorn[standard]"
```


## Usage


According to the FastAPI doc, it is very straitforward : navigate to the MetaMeta directory and execute :

```sh
Bruce@BatDesktop:~/MetaMeta$ uvicorn FastMetAPI:app
```

In the case of a windows machine you need to execute inside bash :

```bash
Robin@WindowsMachine:~/MetaMeta$ python -m uvicorn FastMetAPI:app
```

Bravo ! Now the API is up and running, and ready to accept requests ! Really ? Not really, since the program relly on a PostgreSQL database, which need to be initialized.

## Initialize database

Lets assume you already have an instance of PostgreSQL installed on your device. By default, there are already a database and a user named **postgres**.

On a Unix system, you need to log into the database with <code>sudo -u postgres psql </code>  and then run these SQL commands, replacing *\<password\>* and *\<user\>*  with your own you'll then place into the .env file.
```SQL
CREATE USER <user> WITH ENCRYPTED PASSWORD <password>;
CREATE DATABASE cache;
GRANT ALL PRIVILEGES ON DATABASE cache TO <user>;
```

Then you can initialize the database by running :

```console
Bruce@BatDesktop:~/MetaMeta$ psql -U einstein -d cache < init_db.sql
```

*note : einstein password is 'Niels Bohr ist ein verdammter Idiot', but don't tell anyone*

Now MetAPI is ready to receive requests, and to efficiently process them using the postgreSQL database as a cache. You can at any point kill the app using **ctrl+c** ; just be careful, on some systems this is *coincidentally* also a shortcut for copying stuff. Not that we do that often.

On the client side : How to use MetAPI ?
=====================

Direct use of the API
------------

### Searches

Once the API is up, all you want is send requests. You can adjust the value of **your_query** and **nb_result** as you need to.

```python
import requests
import json

# if you are running MetAPI localy
URL = 'http://127.0.0.1:8000/searches/'

your_query = "mads mikkelsen"
nb_result = 4

headers = {'accept': 'application/json'}

params = (
    ('data', your_query),
    ('nb_result', str(nb_result))
)

response = requests.get('http://127.0.0.1:8000/searches', headers=headers, params=params)
if response.status_code != 200:
    raise Exception(response.status_code, response.text)
else:
    print(json.dumps(response.json(), indent=4, sort_keys=True, ensure_ascii=False))
```

Or you can use a cURL command, replacing "your+query" with...well your actual query. Just replace all spaces with '+'. **Nb_result** is default to 5.

```sh
curl --request GET 'http://127.0.0.1:8000/searches?data=your+query'
```

Because the output is unreadable, you can prettify it using :

```command
curl --request GET 'http://127.0.0.1:8000/searches?data=your+query' | json_pp
```


### Configuration

If you want to configure MetAPI, you need to send a PUT request to the *config* endpoint. The parameters are :
- engines : The name of the engines you want to use
- purge : if you want to empty the cache after the change. Default is 1, in order to avoid conflicts between cache and the actual requests.

exemple of a valid curl request :

```command
curl --request PUT 'http://127.0.0.1:8000/config?engines=Twitter+CNRTL&purge=1'
```

### Cross engine sorting

Also, you may want MetAPI to sort engines between some of them, as if they were into the same topic.
For this, you need to set an environment variable. Just send a json to the */config/cross_engine* endpoint, with this precise structure :

```python
import requests

URL = 'http://127.0.0.1:8000/config/cross_engine'

headers = {'accept': 'application/json'}

data = {'merge' : True, 
        'engines' : {'expert' : "GoogleScholar Twitter"}}

response = requests.post(URL, headers=headers, json=data)
```

### Statistics

If you want to get some insight on the actual usage of MetaMeta, you will need to access it's internal statistics. Just send a request to the */statistics* endpoint. The parameters are :
- <code>raw</code> : If you want all data, you can specify  <code>raw=1</code>. Default is 0. 
- <code>top_query</code> : If you only want to know the top 100 queries, set <code>top_query=100</code>

An exemple of a valid curl command to */statistics*

```command
curl --request GET 'http://127.0.0.1:8000/statistics?top_query=100' | json_pp
```

### Healthcheck

This endpoint is only here to serve testing purposes. If you're unsure wether or not MetAPI is up, just call */healthcheck*.

```sh
Bruce@BatDesktop:~$ echo -e $(curl -s --request GET 'http://127.0.0.1:8000/healthcheck')
"Tout va pour le mieux dans le meilleur des mondes - Pangloss"
```

If by any chance MetAPI is quoting Shakespeare, you're in trouble. It means you don't have the correct information to connect to the database. It will require manual editing of the *.env* file.


```bash
Bruce@BatDesktop:~$ echo -e $(curl -s --request GET 'http://127.0.0.1:8000/healthcheck')
"
	ANTONY
 
 Friends, Romans, countrymen, lend me your ears;
 I come to bury Caesar, not to praise him.
 The evil that men do lives after them;
 The good is oft interred with their bones;
 So let it be with Caesar."
```


Use MetAPI *via* the interface
---------------

### Start the Pyinquirer interface

If you're not in the mood for curl commands, you'll be better off using the interface.

```sh
Bruce@BatDesktop:~/MetaMeta$ python3 __main__.py
```