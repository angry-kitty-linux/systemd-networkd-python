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

from writes import input_y_n

from config import path_dhcp
from config import path_wireless
from config import devnull

from wrappers import Check_error


@Check_error()
def check_root():
    user = getpass.getuser()  # Узнаем пользователя

    if user != "root":
        print_arr("Привет, ", user, color = "green")
        print_arr("Для работоспособности программы Вам требуется root", color = "red")
        exit()


@Check_error()
def device():
    global device

    devices = [line for line in psutil.net_if_stats()]
    device_list = [line for line in devices if line != 'lo']

    if len(device_list) == 1:
        device = device_list[0]
    else:
        device = input_list(
                            "Обнаружено несколько модулей WI-FI, выберите нужный!",
                            device_list,   # Список с модулями
                            color = "yellow"
                            )

        device = device_list[device - 1]  # В функции отчет выполняется с 1,
                                          # поэтому `- 1`


@Check_error()
def write_dhcp(print_output = True):  # Функция, для создания конфига в systemd-networkd
    if print_output is True:
        print_arr("Удаляю конфигурацию...", color = "green")

    with open(path_dhcp, 'w') as f:
        f.write("""
[Match]
Name=en*

[Network]
DHCP=yes
        """)


@Check_error()
def check_pip() -> int:
    """
    Думаю из названия функции все ясно)
    """

    try:
        subprocess.check_call(["pip"], stdout = devnull, stderr = devnull)
        return 1
    except FileNotFoundError:
        return 0


@Check_error()
def distribution() -> str:
    """
    Определение дистрибутива
    """

    with open("/etc/os-release") as f:
        r = f.read()
        distr = r[r.find('NAME="') + 6 :r.find("\n") - 1]

    return distr


@Check_error()
def check_distutils() -> int:
    """
    Для определения модуля distutils (нужен для установки pip)
    """
    try:
        import distutils
        return 1

    except ModuleNotFoundError:
        return 0


@Check_error()
def status_function():
    global psutil

    """
    Функция для того, чтобы сообщить всем остальным
    использовать локальную версию
    """

    try:
        try:
            import psutil
        except ModuleNotFoundError:
            print_arr("Psutil не найден в системе! Устанавливаю...", color = "red")
            if check_connect(timeout=0, print_output = False):

                print_arr("Установочные файлы готовы к сборке!", color = "green")
                print_arr("Идет сборка модуля...", color = "yellow")
                subprocess.check_call(
                                    ["bash", "install_psutil.sh"],
                                    stdout = devnull,
                                    stderr = devnull
                                    )
                print_arr("Модуль psutil - установлен.", color = "green")
                print_arr("Теперь снова запустите этот скрипт!", color = "yellow")
                exit()
            else:
                print_arr("Отсутсвует соединение с интернетом. Использую локальную версию...", color = "yellow")
                import psutil_loc as psutil

        device()

    except Exception as e:
        print_arr(e, color = "red")
        print_arr("Произошла ошибка! Использую локальную версию!", color = "yellow")
        import psutil_loc as psutil


@Check_error()
def write_wireless(
                    print_output = True,
                    replace:bool = False):

    replace:"Перезаписывать ли конфиг"

    if replace is True:
        if print_output is True:
            print_arr("Удаляю конфиг...", color = "green")
        os.remove(path_wireless)

    with open(path_wireless, "w") as f:
        f.write(f"""
[Match]
Name={device}
[Network]
DHCP=ipv4
""")


#@Check_error()
def write_profile(ssid:str, password:str, replace = False) -> bool:
    path = f"/etc/wpa_supplicant/wpa_supplicant-{ssid}-{device}.conf"
    if not os.path.exists(path) or replace is True:
        with open(path, "w") as f:
            ssid, password = (str(ssid), str(password))
            output = os.popen(f"wpa_passphrase {ssid} {password}").read()
            f.write(f"""
ctrl_interface=/run/wpa_supplicant GROUP=wheel
update_config=1
{output}
""")
        write_profile.__annotations__["device"] = device
        write_profile.__annotations__["path"] = path

        return True


@Check_error()
def ppid() -> int:
    for proc in psutil.pids():
        proc = psutil.Process(proc)
        if 'wpa_supplicant' == str(proc.name()):
            return proc.pid


@Check_error()
def check_service() -> int:
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if "wpa_supplicant_python.service" in p.name():
            return 1
    return 0


@Check_error()
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


@Check_error()
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


@Check_error()
def default_locale() -> int:

    """
    Функция для установки дефолтного шрифта
    """

    subprocess.check_call(["setfont"])


@Check_error()
def check_locale() -> int:
    with open("/etc/locale.gen", "r") as f:
        if "#ru_RU.UTF-8 UTF-8" in f.read():
            return 1
        else:
            return 0


@Check_error()
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


