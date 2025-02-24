import psutil
from connect import database
import GPUtil
from time import sleep
from time import time

def avg(lst):
    return sum(lst) / len(lst)
# print(f"{avg(psutil.cpu_percent(interval=0.5, percpu=True))}%")
def get_cpu_percent():
    return avg(psutil.cpu_percent(interval=0.5, percpu=True))
def get_mem_percent():
    return psutil.virtual_memory().percent

def get_mem_total():
    return psutil.virtual_memory().total/(1024*1024)

def get_mem_used():
    return psutil.virtual_memory().used/(1024*1024)

disk_io_start = psutil.disk_io_counters()
last_time = time()
def get_disk_io_rate():
    global disk_io_start, last_time
    disk_io_end = psutil.disk_io_counters()
    current_time = time()
    read_bytes = disk_io_end.read_bytes - disk_io_start.read_bytes
    write_bytes = disk_io_end.write_bytes - disk_io_start.write_bytes

    read_rate = read_bytes / (current_time - last_time)
    write_rate = write_bytes / (current_time - last_time)

    disk_io_start = disk_io_end
    last_time = current_time
    return read_rate, write_rate

net_io_start = psutil.net_io_counters()
last_time_net = time()
def get_network_traffic():
    global net_io_start, last_time_net
    net_io_end = psutil.net_io_counters()
    current_time = time()
    send_bytes = net_io_end.bytes_sent - net_io_start.bytes_sent
    recv_bytes = net_io_end.bytes_recv - net_io_start.bytes_recv
    
    send_rate = send_bytes / (current_time - last_time_net)
    recv_rate = recv_bytes / (current_time - last_time_net)
    
    net_io_start = net_io_end
    last_time_net = current_time
    return send_rate, recv_rate

def get_gpu():
    """
    Returns: gpu load, gpu memory percentage, gpu memory used, gpu memory total, gpu temperature
    """
    GPUs = GPUtil.getGPUs()
    if len(GPUs) == 0:
        return 0, 0
    else:
        return GPUs[0].load, GPUs[0].memoryUtil, GPUs[0].memoryUsed, GPUs[0].memoryTotal, GPUs[0].temperature
    
def main(ip:str="127.0.0.1", port:int=3306, user:str="node1", pwd:str="mysql114514", data_base:str="grafana", log_file:str="log/transformer.log", flush:int=10):
    db = database(
        ip=ip,
        port=port,
        user=user,
        pwd=pwd,
        database=data_base,
    )
    while True:
        cpu_percent = get_cpu_percent()
        mem_percent = get_mem_percent()
        gpu_load, gpu_mem_percent, gpu_mem_used, gpu_mem_total, gpu_temp = get_gpu()
        db.exec(
            f"""INSERT INTO {data_base}.gauge (time, cpu, mem, gpu_load, gpu_mem) VALUES (NOW(), {cpu_percent}, {mem_percent}, {gpu_load}, {gpu_mem_percent});"""
        )
        db.exec(
            f"""INSERT INTO {data_base}.memory (time, total, used) VALUES (NOW(), {get_mem_total()}, {get_mem_used()});"""
        )
        db.exec(
            f"""INSERT INTO {data_base}.gpumem (time, total, used) VALUES (NOW(), {gpu_mem_total}, {gpu_mem_used});"""
        )
        sleep(flush)
        read_rate, write_rate = get_disk_io_rate()
        db.exec(
            f"""INSERT INTO {data_base}.diskio (time, read_rate, write_rate) VALUES (NOW(), {read_rate / 1024/1024}, {write_rate / 1024/1024});"""
        )
        send_rate, recv_rate = get_network_traffic()
        db.exec(
            f"""INSERT INTO {data_base}.netio (time, send_rate, recv_rate) VALUES (NOW(), {send_rate / 1024/1024}, {recv_rate / 1024/1024});"""
        )


if __name__ == "__main__":
    main()
