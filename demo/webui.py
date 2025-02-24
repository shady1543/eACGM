from eacgm.webui import log_reader, database, push_log

ip = "127.0.0.1"
port = 3306
user = "node1"
pwd = "mysql114514"
data_base = "grafana"
table = "CudaEvent"

if __name__ == "__main__":
    log_file = "log/transformer.log"
    
    log = log_reader(log_file)
    db = database(ip, port, user, pwd, data_base)
    push_log(db, log)