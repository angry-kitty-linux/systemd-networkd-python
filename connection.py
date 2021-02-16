#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from colors import print_arr
from daemon import write_daemon
import subprocess
import time
from typing import Union
import writes
from input_while import input_y_n


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


def kill_internet(ppid:int, print_output = True) -> int:
    print_output: "Печать вывода"
    ppid: "Номер процесса"

    status_user = input_y_n("Обнаружено соединение с использование wpa_supplicant, прервать? (y, n)", color = "yellow")
    if status_user == 1:
        writes.kill(ppid)
        if print_output is True:
            print_arr("Соединение было разорвано!", color = "red")
        return 1

    if status_user == 0:
        if print_output is True:
            print_arr("Учтите, т.к wpa_supplicant запущен, могут возникнуть проблемы", color = "red")
        return 0
                


