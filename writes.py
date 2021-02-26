#!/usr/bin/python
# -*- coding: utf-8 -*-

import getpass
from colors import print_arr
from input_while import input_y_n
from input_while import input_list 
import os
from connection import check_connect
from typing import Union
import subprocess
import re
import shutil
import sys

path_dhcp = "/etc/systemd/network/50-dhcp.network"
path_wireless = "/etc/systemd/network/25-wireless.network"

devnull = open(os.devnull, "wb")

def check_root():
    user = getpass.getuser() # Узнаем пользователя

    if user != "root":
        print_arr(f"Привет, ", user, color = "green")
        print_arr("Для работоспособности программы Вам требуется root", color = "red")
        exit()


def device():

    global device

    devices = [line for line in psutil.net_if_stats()]
    device_list = [line for line in devices if line != 'lo']

    if len(device_list) == 1:
        device = device_list[0]
    else:
        device = input_list("Обнаружено несколько модулей WI-FI, выберите нужный!", 
                   device_list,   # Список с модулями
                   color = "yellow")

        device = device_list[device - 1] # В функции отчет выполняется с 1, поэтому `- 1`


def write_dhcp(): # Функция, для создания конфига в systemd-networkd  
    with open(path_dhcp, 'w') as f:
        f.write("""
[Match]
Name=en*
 
[Network]
DHCP=yes
        """)

def check_pip() -> int:
    """
    Думаю из названия функции все ясно)
    """

    try:
        subprocess.check_call(["pip"], stdout = devnull, stderr = devnull)
        return 1
    except FileNotFoundError:
        return 0


def distribution() -> str:
    """
    Определение дистрибутива
    """
    
    with open("/etc/os-release") as f:
        r = f.read()
        distr = r[r.find('NAME="') + 6 :r.find("\n") - 1]
    
    return distr


def check_distutils() -> int:
    """
    Для определения модуля distutils (нужен для установки pip)
    """
    modules = sys.modules.keys()
    for module in modules:
        if module == "distutils": return 1 
        else: 
            return 0


def status_function():
    global psutil

    """
    Функция для того, чтобы сообщить всем остальным использовать локальную версию
    """
    try:
        try:
            import psutil 
        except ModuleNotFoundError:
            print_arr("Psutil не найден в системе!", color = "red")
            if check_connect(timeout = 0, print_output = False):
                if check_pip() == 0:
                    print_arr("Pip не найден, загружаю...", color = "green")
                    subprocess.check_call(["wget", "https://bootstrap.pypa.io/get-pip.py"],
                                          stdout = devnull, stderr = devnull)
                    if check_distutils() == 1:
                        subprocess.check_call(["python3", "get-pip.py"],
                                            stdout = devnull, stderr = devnull)
                    else:
                       distr = distribution()
                       if distr == "Ubuntu" or distr == "Debian":
                           subprocess.check_call(["apt", "install", "python3-distutils"],
                                                 stdout = devnull, stderr = devnull)

                       if check_distutils() == 1:
                           subprocess.check_call(["python3", "get-pip.py"],
                                                 stdout = devnull, stderr = devnull)

                subprocess.check_call(["pip", "install", "psutil"],
                                      stdout = devnull, stderr = devnull)     
                import psutil
                os.remove("get-pip.py")                
                print_arr("Модуль psutil - установлен.", color = "green")
            else:
                print_arr("Отсутсвует соединение с интернетом. Использую локальную версию...", color = "yellow")
                import psutil_loc as psutil
    
        device()

    except Exception as e:
        print_arr(e, color = "red")
        print_arr("Произошла ошибка! Использую локальную версию!", color = "yellow")
        import psutil_loc as psutil

def write_wireless():
    with open(path_wireless, "w") as f:
        f.write(f"""
[Match]
Name={device}
[Network]
DHCP=ipv4
""")


def write_profile(ssid:str, password:str, replace = False) -> bool:
    path = f"/etc/wpa_supplicant/wpa_supplicant-{ssid}-{device}.conf"
    if not os.path.exists(path) or replace is True:
        with open(path, "w") as f:
            ssid, password = (str(ssid), str(password))
            output = os.popen(f"wpa_passphrase {ssid} {password}").read()
            f.write(f"""
ctrl_interface=/run/wpa_supplicant
update_config=1
{output}
""")    
        write_profile.__annotations__["device"] = device
        write_profile.__annotations__["path"] = path
        
        return True


def ppid() -> int:
    for proc in psutil.pids():
        p = psutil.Process(proc)
        if 'wpa_supplicant' == str(p.name()):
            return p.pid


def check_service() -> int:
    known_cgroups = set()
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if "wpa_supplicant_python.service" in p.name(): 
            return 1
    return 0

def extra_kill() -> int:
    
    """
    Функции для просмотра /run/wpa_supplicant
    """
    
    if os.path.exists("/run/wpa_supplicant"):
        shutil.rmtree("/run/wpa_supplicant")
        os.remove("/run/wpa_supplicant")
        return 1
    else:
        return 0


def kill(id_proccess: int) -> int:
    id_proccess: "Айди процесса, для убийства"

    try:
        
        if check_service() == 1:
            subprocess.check_call(["systemctl", "stop", "wpa_supplicant_python.service"], 
                                    stderr = devnull, stdout = devnull)
        
        process = psutil.Process(id_proccess)
        process.kill()
        
        if check_connect(timeout = 1.5, print_output = False) == 1:
            status_kill = extra_kill()
        
            if status_kill == 0:
                print_arr("Не получилось отключится, прерывание!", color = "red")
                exit()

        return 1
    except:
        return 0


def default_locale() -> int:
    
    """
    Функция для установки дефолтного шрифта
    """

    subprocess.check_call(["setfont"])


def check_locale() -> int:
    with open("/etc/locale.gen", "r") as f:
        if "#ru_RU.UTF-8 UTF-8" in f.read():
            return 1
        else:
            return 0


def russian_locale() -> int:
    
    """
    Это функция для установки русской локали
    (Чтобы не было квадратиков в tty)
    """

    try:
        if check_locale() == 1:
            with open("/etc/locale.gen", "r") as f:
                file_read = f.read()
        
            open("/etc/locale.gen", "w").close()

            with open("/etc/locale.gen", "w") as f:
                file_read = file_read.replace("#ru_RU.UTF-8 UTF-8", "ru_RU.UTF-8 UTF-8")
                print(file_read, file = f)

            subprocess.check_call(["locale-gen"])
        
        subprocess.check_call(["setfont", "latarcyrheb-sun16"], stderr=devnull)

        return 1
    except (FileNotFoundError, subprocess.CalledProcessError) :
        return 0 


