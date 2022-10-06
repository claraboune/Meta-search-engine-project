from fastapi import FastAPI, Request
import os
import dotenv
# import asyncio
import psycopg2
from pydantic import BaseModel

from MetAPI.process import Process

class Config_params(BaseModel):
    merge: bool = None
    engines: dict


app = FastAPI()


@app.get("/")
def read_root():
    return {"The Cure": "BUILD MORE HOUSING !"}


@app.get("/statistics")
def get_statistics(top_query: int = 10, raw: int = 0):
    process = Process()
    if raw:
        return {"stats": process.raw_stats()}
    return process.get_stats(top_query=top_query)


@app.get("/healthcheck")
def healthcheck():
    # with Process().check_connection as process:
    # don't know with this syntax isn't working, if you do
    # please reach me at : timothee@obrecht.xyz
    process = Process()
    dotenv.load_dotenv(override=True)
    try:
        psycopg2.connect(
            dbname=os.environ["DATABASE"],
            user=os.environ["USER"],
            host=os.environ["HOST"],
            port=os.environ["PORT"],
            password=os.environ["PASSWORD"]
        )
    except psycopg2.OperationalError:
        return r"""\n\tANTONY

            Friends, Romans, countrymen, lend me your ears;
            I come to bury Caesar, not to praise him.
            The evil that men do lives after them;
            The good is oft interred with their bones;
            So let it be with Caesar."""
    process = process.check_connection()
    if process is Exception:
        return process
    if not(process):
        return Exception("Database error", "Database is down")
    return """Tout va pour le mieux dans le meilleur des mondes - Pangloss"""


@app.get("/searches")
async def search(data: str, request: Request, nb_result:int = 5):
    ip = request.client.host
    # data is users's query here
    process = Process()
    if len(data) == 0:
        return {}
    result = process.checkCache(data, ip)
    if result is Exception:
        return str(result)
    if result is None:
        print("Not in cache")
        # useless if search is itself async, but if not :
        # result = asyncio.run(process.makeSearch(data))
        result = await process.makeSearch(data, nb_result=nb_result)
        result = process.sortTogether()
        process.addCache(data, result)
    return result


@app.put("/config")
def config(engines: str = None, purge: int = 1, date = None):
    if engines:
        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file)
        os.environ["ENGINE_LIST"] = engines
        dotenv.set_key(dotenv_file, "ENGINE_LIST", os.environ["ENGINE_LIST"])
    if purge:
        process = Process()
        process.purgeCache(date)
    return


@app.post("/config/cross_engine")
def cross_engine_config(params: Config_params):
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    os.environ["CROSS_ENGINE_PARAMS"] = params.json()
    dotenv.set_key(dotenv_file, "CROSS_ENGINE_PARAMS",
                   os.environ["CROSS_ENGINE_PARAMS"])
    return
