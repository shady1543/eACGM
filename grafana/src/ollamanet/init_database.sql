DROP Table IF EXISTS grafana.ollamanet;
DROP TABLE if EXISTS grafana.ipport;
CREATE TABLE IF NOT EXISTS grafana.ollamanet
(
    time DATETIME,
    request DOUBLE,
    token DOUBLE
);
CREATE TABLE IF NOT EXISTS grafana.ipport
(
    ipport CHAR(255) PRIMARY KEY,
    cnt INT
);