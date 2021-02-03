#!/usr/bin/python

import os
from colors import print_arr
from daemon import write_daemon
import subprocess
import time
from typing import Union
import writes


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

    while True:
        user_choice = input("> ")
        if user_choice == "y":
            writes.kill(ppid)
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

def russian_locale() -> int:
    """
    Это функция для установки русской локали
    (Чтобы не было квадратиков в tty)
    """

    with open("/etc/locale.gen", "r+") as f:
        read_file = f.read()

        find_locale = [True for line in f.readlines() if line == "ru_RU.UTF-8 UTF-8"]
        if find_locale == []:
            f.write("\nru_RU.UTF-8 UTF-8")

