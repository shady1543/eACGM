import time
import os
import argparse
from connect import database

interval = 5
max_time = 0

def tail_f(args, db, filename):
    with open(filename, 'r') as file:
        # 移动文件指针到文件末尾
        file.seek(0, 2)
        global max_time
        while True:
            # 读取新行
            line = file.readline()
            
            if not line:
                time.sleep(1)  # 如果没有新行，暂停一秒后继续检查
                ts = int(time.time())
                if ts - max_time > interval:
                    db.exec(f"""INSERT INTO {args.database}.ollamanet VALUES (NOW(), 0, 0)""")
                    max_time = ts
                continue
            
            yield line

def main(db:database, args):
    global interval, max_time
    log_file = args.file
    interval = args.interval
    if not os.path.exists(log_file):
        os.system(f"touch {log_file}")
    buf = []
    for line in tail_f(args, db, log_file):
        line = line.strip()
        if line.strip() == "---":
            l0 = buf[0].split(' ')
            ts = int(l0[0])
            max_time = max(max_time, ts)
            cnt = int(l0[1]) / interval
            l1 = buf[1].split(' ')
            recv = int(l1[0]) / interval
            send = int(l1[1]) / interval
            # print(f"{ts} {cnt} {recv} {send}")
            # print(buf)
            db.exec(f"""INSERT INTO {args.database}.ollamanet VALUES (NOW(), {recv}, {send});""")
            i = 2
            while i < len(buf) - 1:
                l = buf[i].split(' ')
                ipport = l[0]
                ipport = ipport[:ipport.rfind('.')]
                i += 1
                if ipport == args.local:
                    continue
                cnt = int(l[1])
                
                all = db.exec(f"""SELECT cnt from {args.database}.ipport where ipport='{ipport}';""")
                
                if not all:
                    all = cnt
                    db.exec(f"""INSERT INTO {args.database}.ipport VALUES ('{ipport}', {cnt});""")
                else:
                    all = all[0][0]
                    all += cnt
                    db.exec(f"""UPDATE {args.database}.ipport SET cnt={all} where ipport='{ipport}';""")
            buf = []
            continue
        buf.append(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, default='trace.txt', help='log file')
    parser.add_argument('--interval', type=int, default=5, help='interval (s)')
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='ip')
    parser.add_argument('--port', type=int, default=3306, help='port')
    parser.add_argument('--user', type=str, default='node1', help='user')
    parser.add_argument('--password', type=str, default='mysql114514', help='password')
    parser.add_argument("--database", type=str, default="grafana", help="database")
    parser.add_argument("--local", type=str, default="127.0.0.1.11434")
    args = parser.parse_args()
    db = database(args.ip, args.port, args.user, args.password, args.database)
    main(db, args)
            
