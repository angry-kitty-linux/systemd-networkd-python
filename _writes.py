#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Этот модуль сделан для взаимодействия с профилями.
Его функции создавать/изменять файлы и т.д
"""

from typing import Union, List, Tuple
import subprocess
import sys
import getpass
import os
import psutil

from _colors import print_arr

from _input_while import input_y_n
from _input_while import input_list
from _input_while import password_user

from _connection import check_connect

from _config import path_dhcp
from _config import path_wireless
from _config import path_module
from _config import path_Wpa
from _config import devnull

from _wrappers import Check_error
from _wrappers import KeyboardError


@Check_error()
def check_root():
    user = getpass.getuser()  # Узнаем пользователя

    if user != "root":
        print_arr("Привет, ", user, color="green")
        print_arr("Для работоспособности программы Вам требуется root", color="red")
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
                            color="yellow"
                            )
    return device


@Check_error()
def write_dhcp(print_output=True):  # Функция, для создания конфига в systemd-networkd
    if print_output is True:
        print_arr("Удаляю конфигурацию...", color="green")

    with open(path_dhcp, 'w') as f:
        f.write("""
[Match]
Name=en*

[Network]
DHCP=yes
        """)


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
def write_wireless(print_output: bool=True, replace: bool=False):
    if replace is True:
        if print_output is True:
            print_arr("Удаляю конфиг...", color="green")
        os.remove(path_wireless)

    with open(path_wireless, "w") as f:
        f.write(f"""
[Match]
Name={device}
[Network]
DHCP=ipv4
""")



def write_profile(ssid:str, password:str, replace=False) -> Union[bool, str]:
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
        subprocess.check_call(
                            ["chmod", "733", path],
                            stdout=devnull,
                            stderr=devnull
                            )      # Отбираем права на чтение

        write_profile.__annotations__["device"] = device
        write_profile.__annotations__["path"] = path

        return True
    
    if os.path.exists(path):
        return path

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
    """ Функции для выключения wpa_supl """

    try:
        subprocess.check_call(["wpa_cli", "disconnect"],
                              stdout=devnull,
                              stderr=devnull
        )

        os.remove("/run/wpa_supplicant/{}".format(device))

        return 1
    except Exception:
        return 0


@Check_error()
def kill(id_proccess: int) -> int:
    """ Завершение процесса """

    try:
        process = psutil.Process(id_proccess)
        process.kill()

        if check_connect(timeout=1.5, print_output=False) == 1:
            status_kill = extra_kill()

            if status_kill == 0:
                print_arr("Не получилось отключится, прерывание!",
                          color="red")
                exit()

        return 1
    except Exception as e:
        print_arr (e, color="red")
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
                print(file_read, file=f)

            subprocess.check_call(["locale-gen"])

        subprocess.check_call(["setfont", "latarcyrheb-sun16"], stderr=devnull)

        return 1
    except (FileNotFoundError, subprocess.CalledProcessError):
        return 0


@KeyboardError()
@Check_error()
def module_profile():
    """ Для создания профиля модуля """

    _config_info = """
ctrl_interface=/run/wpa_supplicant
update_config=1"""

    try:
        with open(path_module, "r") as f:
            if f.read() != _config_info:
                raise FileNotFoundError
    except FileNotFoundError:
        with open(path_module, "w") as f:
            print(_config_info, file=f)

    subprocess.check_call(
                        ["systemctl", "restart", "wpa_supplicant"],
                        stdout=devnull,
                        stderr=devnull
    )


def profiles_mkdir() -> List[str]:
    """ Поиск профилей в /etc/wpa_supplicant """

    profiles = os.listdir("/etc/wpa_supplicant")
    profiles_mk = []
    for line in profiles:
        begin_ind = line.find("-") + 1  # Начальный индекс
        end_ind = line.rfind("-")  # Конечный индекс
        if end_ind == -1: continue

        index = slice(begin_ind, end_ind)
        profiles_mk.append(line[index])

    return profiles_mk


def view_password(profile: str) -> Union[str, None]:
    """ Просмотр пароля в профиле """
    
    files = os.listdir(path_Wpa)
    
    count_True = sum([True for file in files if profile in file])
    profiles = [file[15:-5] for file in files if profile in file]
    
    # Для определения кол-ва найденных профидей (во избежание путаницы)
    if count_True != 1:
       user_Choice = input_list("Обнаружен профиль с разными модулями WI-FI"
                                ", выберите нужный",
                                profiles,
                                color="yellow") 
    if count_True == 1:
        user_Choice = profiles[0]

    path = f"{path_Wpa}/wpa_supplicant-{user_Choice}.conf"

    with open(path, "r") as file:
        for line in file:
            if "#psk" in line:
                password = line[7:-2]
    
    if count_True is None:
        password = None

    return password


def password_and_ssid() -> Tuple[str]:
    """ Функция для ввода SSID & Пароля """

    # Ввод ssid
    print_arr("Введите SSID (название точки доступа)", color="green")
    ssid = input("> ")
    # Ввод пароля
    if ssid in profiles_mkdir():
        user_Choice = input_y_n("Профиль существует, перезаписать? (y, n) ",
                                color="yellow") 
        if user_Choice == 0:
           password = view_password 

    password = password_user(ssid)
    return ssid, password




