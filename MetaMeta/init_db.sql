CREATE SEQUENCE id_stat_seq as integer increment by 1
minvalue 1 start with 1;

DROP TABLE IF EXISTS Requete;
CREATE TABLE Requete (
    params varchar(256) PRIMARY KEY,
    latest_query timestamp,
    results json
);

DROP TABLE IF EXISTS Statistique;
CREATE TABLE Statistique (
    id_stat integer default nextval('id_stat_seq') PRIMARY KEY,
    params varchar(256),
    ip_adress varchar(256),
    date timestamp
);
