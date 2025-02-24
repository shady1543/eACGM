DROP TABLE IF EXISTS grafana.gauge;
DROP TABLE IF EXISTS grafana.memory;
DROP TABLE IF EXISTS grafana.gpumem;
DROP TABLE IF EXISTS grafana.diskio;
DROP TABLE IF EXISTS grafana.netio;
CREATE Table IF NOT EXISTS grafana.gauge(
    TIME DATETIME,
    cpu DOUBLE,
    mem DOUBLE,
    gpu_load DOUBLE,
    gpu_mem DOUBLE
);
CREATE TABLE IF NOT EXISTS grafana.memory(
    TIME DATETIME,
    total DOUBLE,
    used DOUBLE
);
CREATE TABLE IF NOT EXISTS grafana.gpumem(
    TIME DATETIME,
    total DOUBLE,
    used DOUBLE
);
CREATE TABLE IF NOT EXISTS grafana.diskio(
    TIME DATETIME,
    read_rate DOUBLE,
    write_rate DOUBLE
);
CREATE TABLE IF NOT EXISTS grafana.netio(
    TIME DATETIME,
    send_rate DOUBLE,
    recv_rate DOUBLE
);