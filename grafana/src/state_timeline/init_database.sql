-- WARNING: database grafana will be cleared if exists
DROP DATABASE IF EXISTS grafana;
CREATE DATABASE IF NOT EXISTS grafana;
drop TABLE if EXISTS grafana.CudaEvent;
CREATE TABLE IF NOT EXISTS grafana.CudaEvent(
    time DOUBLE,
    event1 CHAR(255),
    event2 CHAR(255),
    event3 CHAR(255)
);
CREATE TABLE IF NOT EXISTS grafana.events(
    name CHAR(255) PRIMARY KEY,
    cnt INT
);