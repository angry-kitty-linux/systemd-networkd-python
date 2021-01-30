#!/usr/bin/python

import os
from colors import print_arr
import subprocess
import time
import psutil
from typing import Union

def check_connect(timeout = 10, print_output = True) -> int:
    
    timeout: "Задержка (wpa_supplicant не сразу включается)"
    print_output: "Печатать вывод"

    try:
        if print_output is True:
            print_arr("Проверка соединения...", color = "yellow")
        
        time.sleep(timeout)
        dev_null = open(os.devnull, 'wb')

        subprocess.check_call(["ping", "-c 1", "eth0.me"], stdout=dev_null, stderr = dev_null)
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

def ppid() -> Union[int]:
    for proc in psutil.pids():
        p = psutil.Process(proc)
        if 'wpa_supplicant' in str(p.name):
            return p.pid
        
def kill(id_proccess: int) -> int:
    try:
        id_proccess: "Айди процесса, для убийства"
        process = psutil.Process(id_proccess)
        process.kill()
        return 1
    except:
        return 0


def kill_internet(ppid:int, print_output = True) -> int:
    print_output: "Печать вывода"
    ppid: "Номер процесса"

    while True:
        user_choice = input("> ")
        if user_choice == "y":
            kill(ppid)
            if print_output is True:
                print_arr("Соединение было разорвано!", color = "red")
            return 1
            break

        if user_choice == "n":
            if print_output is True:
                print_arr("Учтите, т.к wpa_supplicant запущен, могут возникнуть проблемы", color = "red")
            return 1
            break
                
        else:
            print_arr("Не понимаю о чем Вы, повторите еще раз...", color = "red")
            return 0

def autostart_wpa() -> int:
    subprocess.check_call(["systemctl", "enable", ""], stdout=dev_null, stderr = dev_null)
    
