CREATE USER 'node1' @'%' IDENTIFIED BY 'mysql114514';

GRANT ALL PRIVILEGES ON *.* TO 'node1' @'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;
-- grafana database
CREATE DATABASE IF NOT EXISTS grafana;
-- state timeline
CREATE TABLE IF NOT EXISTS grafana.CudaEvent (
    time DOUBLE,
    event1 CHAR(255),
    event2 CHAR(255),
    event3 CHAR(255)
);

CREATE TABLE IF NOT EXISTS grafana.events (
    name CHAR(255) PRIMARY KEY,
    cnt INT
);
-- top
CREATE Table IF NOT EXISTS grafana.gauge (
    TIME DATETIME,
    cpu DOUBLE,
    mem DOUBLE,
    gpu_load DOUBLE,
    gpu_mem DOUBLE
);

CREATE TABLE IF NOT EXISTS grafana.memory (
    TIME DATETIME,
    total DOUBLE,
    used DOUBLE
);

CREATE TABLE IF NOT EXISTS grafana.gpumem (
    TIME DATETIME,
    total DOUBLE,
    used DOUBLE
);

CREATE TABLE IF NOT EXISTS grafana.diskio (
    TIME DATETIME,
    read_rate DOUBLE,
    write_rate DOUBLE
);

CREATE TABLE IF NOT EXISTS grafana.netio (
    TIME DATETIME,
    send_rate DOUBLE,
    recv_rate DOUBLE
);
-- ollamanet
CREATE TABLE IF NOT EXISTS grafana.ollamanet (
    time DATETIME,
    request DOUBLE,
    token DOUBLE
);

CREATE TABLE IF NOT EXISTS grafana.ipport (
    ipport CHAR(255) PRIMARY KEY,
    cnt INT
);
