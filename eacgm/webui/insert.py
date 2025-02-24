# insert data into mysql database
import argparse
from reader import log_reader
from reader import log_reader
from connect import database
import time

def get_col_num(db) -> int:
    col_num = db.exec(
            f"SELECT COUNT(*) FROM information_schema.COLUMNS where `TABLE_SCHEMA` = 'grafana' and `TABLE_NAME` = 'CudaEvent';"
        )
    col_num = col_num[0][0]
    return col_num

def lts_cuda_event(db) -> list:
    """to get the latest cuda event before
    """
    ret = db.exec(f"SELECT * FROM grafana.`CudaEvent` ORDER BY time DESC LIMIT 1;")
    # print(ret)
    if len(ret) == 0:
        col_num = get_col_num(db)
        lts_event = [None] * (col_num - 1)
    else:
        lts_event = list(ret[0][1:])
    return lts_event

def lts_event_cnt(db) -> dict:
    """to get the latest data of event count
    """
    ret = db.exec(
        """SELECT * FROM grafana.events;"""
    )
    d = dict()
    for name, cnt in ret:
        d[name] = cnt
    return d

def add_col(db):
    col_num = get_col_num(db)
    db.exec(f"""ALTER TABLE grafana.`CudaEvent` ADD COLUMN event{col_num} CHAR(255)""")

def del_col(db, col_num):
    db.exec(f"""ALTER TABLE grafana.`CudaEvent` DROP COLUMN event{col_num};""")

def add_empty(max_time, db):
    col_num = get_col_num(db)
    db.exec(f"""INSERT INTO grafana.`CudaEvent` VALUES ({max_time}, {','.join(['NULL'] * (col_num - 1))})""")
    
def push_log(db, log):
    max_time = 0
    ## latest cuda event
    cuda_event = lts_cuda_event(db)
    ## latest event cnt
    event_cnt = lts_event_cnt(db)
    cmd = f"INSERT INTO grafana.CudaEvent VALUES " 
    for line_idx, l in enumerate(log):
        if l['op'] == 'start':
            if l['name'] in event_cnt:
                event_cnt[l['name']] += 1
            else:
                event_cnt[l["name"]] = 1
            empty_col = False
            i = 0
            for e in cuda_event:
                if e is None:
                    cuda_event[i] = l['name']
                    empty_col = True
                    break
                i += 1
            if not empty_col:
                if len(cmd) > 37:
                    cmd = cmd[:-1] + ";"
                    # print(cmd)
                    # print('------')
                    db.exec(cmd)
                    cmd = f"INSERT INTO grafana.CudaEvent VALUES "
                add_col(db)
                cuda_event.append(l['name'])
        elif l['op'] == 'end':
            if l['name'] in event_cnt:
                if event_cnt[l["name"]] == 0:
                    print(f"[!]: in line {line_idx + 1}: event {l['name']} ended more than starting")
                    #raise ValueError(f"in line {line_idx + 1}: event {l['name']} ended more than starting")
                    continue
                event_cnt[l["name"]] -= 1
                for i, e in enumerate(cuda_event[::-1]):
                    if e == l["name"]:
                        cuda_event[len(cuda_event)- 1 - i] = None
                        break
            if l["name"] not in event_cnt:
                print(f"[!]: in line {line_idx + 1}: event {l['name']} ended without starting")
                # raise ValueError(f"in line {line_idx + 1}: event {l['name']} ended without starting")
                continue

        else:
            raise ValueError(f"in line {line_idx + 1}: unknown operation {l['op']}")
        tmp_cmd = f"({l['time']}, "
        max_time = max(max_time, float(l['time']))
        for e in cuda_event:
            if e is None:
                tmp_cmd += "NULL, "
            else:
                tmp_cmd += f"'{e}', "
        tmp_cmd = tmp_cmd[:-2] + "),"
        cmd += tmp_cmd
    if len(cmd) > 37:
        cmd = cmd[:-1] + ";"
        # print(cmd)
        # print("------")
        db.exec(cmd)
    # print(cuda_event)
    # print(event_cnt)
    add_empty(max_time,db)