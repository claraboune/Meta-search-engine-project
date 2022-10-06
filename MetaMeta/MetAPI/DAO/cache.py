from MetAPI.DAO.singleton import Singleton
from MetAPI.DAO.db_connection import DBConnection
import json
from datetime import datetime
import hashlib
import dotenv
import os


class Cache(metaclass=Singleton):

    def __init__(self) -> None:
        pass

    def get(self, user_request, user_ip):
        '''Méthode qui accède à la base de données
        et en extrait les requêtes correspondant à "user_request"
        Met à jour la table statistique en conséquence
        
        Parameters :
        ------------
        user_request : la chaîne de caractères correspondant à la requête
        user_ip : l'adresse ip de l'utilisateur
        
        Returns :
        ---------
        res : ensemble des requêtes correspondant à user_request
        
        Examples :
        ----------
        >>> c=Cache()
        >>> c.put("Sagan","Bonjour tristesse")
        >>> r=c.get("Sagan","127.0.0.1")
        >>> print(r[0]["results"])
        Bonjour tristesse
        '''
        dt = datetime.now()
        key = hashlib.sha224(user_request.encode('utf8')).hexdigest()
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute("""
                INSERT INTO statistique VALUES(nextval('id_stat_seq'),
                %(request)s, %(ip)s, %(dt)s);

                UPDATE Requete SET latest_query=%(dt)s
                WHERE params=%(key)s;

                SELECT * FROM requete
                WHERE params = %(key)s;""", {
                     "key": str(key),
                     "ip": user_ip,
                     "dt": str(dt),
                     "request": user_request
                    })
                    res = cursor.fetchall()
                except Exception as error:
                    return error
        return res

    def put(self, user_request, result):
        '''Méthode qui place un résultat dans la table requête
        
        Parameters :
        ------------
        user_request : chaîne correspondant aux mots-clés de la requête
        result : json correspondant au résultat
        
        Examples :
        ----------
        >>> c=Cache()
        >>> c.put("Aristote","La poétique")
        >>> r=c.get("Aristote","127.0.0.1")
        >>> print(r[0]["results"])
        La poétique
        '''
        dt = datetime.now()
        dotenv.load_dotenv(override=True)
        dbname=os.environ["DATABASE"]
        db_max_size = int(os.environ["DB_MAX_SIZE"])
        key = hashlib.sha224(user_request.encode('utf8')).hexdigest()
        # must check berfore if the key isn't already in use
        # if cache is full, the oldest query is deleted
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                try:
                    
                    cursor.execute(
                        """INSERT INTO requete VALUES (%(key)s,%(dt)s,%(res)s);
                        
                        SELECT * FROM pg_database_size(%(dbname)s);""",
                        {"key": str(key),
                         "dt": str(dt),
                         "res": json.dumps(result),
                         "dbname" : dbname}
                    )
                    res = cursor.fetchall()
                except Exception as error:
                    print(error)
                    return error
                if  res[0]['pg_database_size'] > db_max_size:
                    # delete the five oldest responses
                    cursor.execute("""
                    DELETE FROM requete WHERE params IN 
                    (SELECT params FROM requete ORDER BY latest_query DESC LIMIT 5);
                    """
                    )

    def send_raw_stats(self):
        SQLrequest = "SELECT * FROM statistique ;"
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(SQLrequest)
                except Exception as error:
                    return error
                return cursor.fetchall()

    def get_stats(self, user_request, date1, date2):
        '''Méthode qui renvoie le nombre d'accès à une requête
        entre deux dates
        
        Parameters :
        ------------
        user_request : la chaîne correspondant à la requête
        date1 : date/borne de début pour l'accès à la requête
        date2 : date/borne de fin
        
        Returns :
        ---------
        cursor.fetchall() : dictionnaire contenant le nombre d'accès
        
        Example :
        ---------
        >>> c=Cache()
        >>> c.put("AAAAAA143","Result129")
        >>> r=c.get("AAAAAA143","127.0.0.1")
        >>> d=datetime.now()
        >>> r=c.get_stats("AAAAAA143",d,d)
        >>> print(r[0]["count"])
        0
        '''
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT count(distinct id_stat) from statistique where"
                    " params=%(req)s and date>=%(d1)s and date<=%(d2)s ;",
                    {"req": str(user_request),
                     "d1": str(date1),
                     "d2": str(date2)}
                    )
                return cursor.fetchall()

    def purge(self, date=None):
        '''Méthode qui élimine les requêtes dont la dernière date d'accès
        est antérieure à "date"
        
        Parameters :
        ------------
        date : la date de dernier accès
        
        '''
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                if date:
                    cursor.execute(
                        "DELETE from Requete where latest_query<=%(dt)s",
                        {"dt": str(date)}
                    )
                else:
                    cursor.execute("TRUNCATE TABLE requete;")
