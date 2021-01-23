#!/usr/bin/python

import os
from colors import print_arr
import subprocess
import time
import psutil

def check_connect(timeout = 10, print_output = True) -> int:
    
    timeout: "Задержка (wpa_supplicant не сразу включается)"
    print_output: "Печатать вывод"

    try:
        if print_output is True:
            print_arr("Проверка соединения...", color = "yellow")
        
        time.sleep(timeout)
        subprocess.check_call(["ping", "-c 1", "eth0.me"], stdout=open(os.devnull, 'wb'), stderr = None)
        return 1

    except subprocess.CalledProcessError:
        return 0


def connect(device:str, path:str, print_output = True) -> int:
    device: "Модуль вафли"
    path: "Путь до конфига"
    print_output: "Печатать вывод"

    # Финальный шаг
    command = "wpa_supplicant -B -i {} -c {}".format(device, path)
    output = os.popen(command).read() 
    connect.__annotations__['output'] = output

    if check_connect() == 1:
        if print_output is True:
            print_arr("Подключено!", color = "green")
        return 1 

    else:
        if print_output is True:
            print_arr(output, color = "red")
            print_arr("Не получилось подключится ): ", color = "red")
        return 0

def ppid() -> int:
    for proc in psutil.pids():
        p = psutil.Process(proc)
        if 'wpa_supplicant' in str(p.name):
            return p.pid

def kill(id_proccess: int):
    id_proccess: "Айди процесса, для убийства"
    process = psutil.Process(id_proccess)
    process.kill()
