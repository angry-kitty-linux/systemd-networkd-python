#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Этот модуль сделан для взаимодействия с профилями.
Его функции создавать/изменять файлы и т.д
"""

from typing import Union, List, Tuple
import subprocess
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

import __init__


@Check_error()
def check_root():
    """ Проверка рута """

    user = getpass.getuser()  # Узнаем пользователя

    if user != "root":
        print_arr("Привет, ", user, color="green")
        print_arr("Для работоспособности программы "
                  "Вам требуется root", color="red")
        raise SystemExit(1)


@Check_error()
def take_device(print_output: bool = True) -> Tuple[str]:
    """ Определение вафли """
    global device

    devices = [line for line in psutil.net_if_stats()]
    device_list = [line for line in devices
                   if line != 'lo' and "enp" not in line]

    if len(device_list) == 1:
        device = device_list[0]
        return device

    elif len(device_list) == 0:
        print_arr("Ошибка: Не обнаружено ни одного молуля!", color="red")
        raise SystemExit(1)

    else:
        device_arg = __init__.args.device
        if device_arg is not False:  # Если был введен аргумент --device
            if device_arg not in device_list:  # если пользователь ошибся
                print_arr(f"Модуль {device_arg} не найден!", color="yellow")
                device = input_list("Обнаружено несколько модулей"
                                    " WI-FI, выберите нужный!",
                                    device_list,   # Список с модулями
                                    color="yellow")
            else:   # Если все норм
                device = device_arg

        elif device_arg is False:  # Если аргумента непоследовало
            if print_output is True:
                device = input_list("Обнаружено несколько модулей"
                                    " WI-FI, выберите нужный!",
                                    device_list,   # Список с модулями
                                    color="yellow")

        return device


@Check_error()
def write_dhcp():
    """ Запись dhcp профиля """
    with open(path_dhcp, 'w') as file:
        file.write("""
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

    with open("/etc/os-release") as file:
        read = file.read()
        distr = read[read.find('NAME="') + 6:read.find("\n") - 1]
    return distr


@Check_error()
def write_wireless():
    """ Создания профиля """

    with open(path_wireless, "w") as file:
        file.write(f"""
[Match]
Name={device}
[Network]
DHCP=ipv4
""")



def write_profile(ssid: str,
                  password: Union[str, None],
                  replace=False) -> Union[bool, str]:
    path = f"/etc/wpa_supplicant/wpa_supplicant-{ssid}-{device}.conf"
    if not os.path.exists(path) or replace is True:
        if password is not None:
            with open(path, "w") as file:
                ssid, password = (str(ssid), str(password))
                output = os.popen(f"wpa_passphrase {ssid} {password}").read()
                file.write(f"""
ctrl_interface=/run/wpa_supplicant GROUP=wheel
update_config=1
{output}
""")

        if password is None:
            with open(path, "w") as file:
                ssid = str(ssid)
                file.write('ctrl_interface=/run/wpa_supplicant GROUP=wheel\n'
                           'update_config=1\n'
                           'network={\n'
                           f'ssid="{ssid}"\n'
                           'key_mgmt=NONE\n'
                           '}')

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
        if str(proc.name()) == 'wpa_supplicant':
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
                              stderr=devnull)

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
                raise SystemExit(1)

        return 1
    except Exception as e:
        return 0


@Check_error()
def default_locale() -> int:
    """
    Функция для установки дефолтного шрифта
    """

    subprocess.check_call(["setfont"])


@Check_error()
def check_locale() -> int:
    """ Проверка наличия русской локали """

    with open("/etc/locale.gen", "r") as file:
        if "#ru_RU.UTF-8 UTF-8" in file.read():
            return 1
        return 0


@Check_error()
def russian_locale() -> int:
    """
    Это функция для установки русской локали
    (Чтобы не было квадратиков в tty)
    """

    try:
        if check_locale() == 1:
            with open("/etc/locale.gen", "r") as file:
                file_read = file.read()

            open("/etc/locale.gen", "w").close()

            with open("/etc/locale.gen", "w") as file:
                file_read = file_read.replace("#ru_RU.UTF-8 UTF-8",
                                              "ru_RU.UTF-8 UTF-8")
                print(file_read, file=file)

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
        with open(path_module, "r") as file:
            if file.read() != _config_info:
                raise FileNotFoundError
    except FileNotFoundError:
        with open(path_module, "w") as file:
            print(_config_info, file=file)

    subprocess.check_call(
                        ["systemctl", "restart", "wpa_supplicant"],
                        stdout=devnull,
                        stderr=devnull
    )


@Check_error()
@KeyboardError()
def profiles_mkdir() -> List[str]:
    """ Поиск профилей в /etc/wpa_supplicant """

    profiles = os.listdir("/etc/wpa_supplicant")
    profiles_mk = []
    for line in profiles:
        begin_ind = line.find("-") + 1  # Начальный индекс
        end_ind = line.rfind("-")  # Конечный индекс
        if end_ind == -1:
            continue

        index = slice(begin_ind, end_ind)
        profiles_mk.append(line[index])

    return profiles_mk


@Check_error()
@KeyboardError()
def correct_Profile(profile: str) -> Union[str, None]:
    """ Для определения нужного профиля с одним SSID и с разными модулями """

    files = os.listdir(path_Wpa)
    count_True = sum([True for file in files if profile in file])
    profiles = [file[15:-5] for file in files if profile in file]
    # Для определения кол-ва найденных профидей (во избежание путаницы)
    if count_True != 1 and count_True != 0:
        user_Choice = input_list("Обнаружен профиль с разными модулями WI-FI"
                                 ", выберите нужный",
                                 profiles,
                                 color="yellow")

        path = f"{path_Wpa}/wpa_supplicant-{user_Choice}.conf"

    if count_True == 1:
        user_Choice = profiles[0]
        path = f"{path_Wpa}/wpa_supplicant-{user_Choice}.conf"

    if count_True == 0:
        path = None

    return path


@Check_error()
@KeyboardError()
def view_password(path: str) -> Union[str, None]:
    """ Просмотр пароля в профиле """

    with open(path, "r") as file:
        for line in file:
            if "#psk" in line:
                return line[7:-2]
            return None


@KeyboardError()
def password_and_ssid() -> Tuple[str]:
    """ Функция для ввода SSID & Пароля """

    # Ввод ssid
    print_arr("Введите SSID (название точки доступа)", color="green")
    ssid = input("> ")
    # Ввод пароля

    path = correct_Profile(ssid)
    if ssid in profiles_mkdir():
        user_Choice = input_y_n("Профиль существует, перезаписать? (y, n) ",
                                color="yellow")
        if user_Choice == 0:
            password = view_password(path)
            return ssid, password

        if user_Choice == 1:
            os.remove(path)

    password = password_user(ssid)
    return ssid, password
