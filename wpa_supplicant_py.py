#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Основной файл """


import os
import subprocess
from collections import Counter

import __init__
from _colors import print_arr

from _writes import write_dhcp, write_wireless, write_profile
from _writes import take_device
from _writes import check_root
from _writes import ppid
from _writes import russian_locale
from _writes import module_profile
from _writes import password_and_ssid
from _writes import profiles_mkdir
from _writes import view_password
from _writes import correct_Profile

from _connection import connect
from _connection import check_connect
from _connection import kill_internet

from _daemon import write_daemon

from _input_while import input_y_n
from _input_while import input_list
from _input_while import password_user

from _config import devnull


try:
    russian_locale()
    check_root()
    device_user = take_device()
    # -----------------------

    module_profile()
    write_dhcp()

    #########################
    # Добавление в автозагрузку
    print_arr(
            "Запускаю/добавляю в автозагрузку systemd-networkd...",
            color="pink")

    subprocess.check_call(["systemctl", "enable", "--now",
                          "systemd-networkd.service"],
                          stdout=devnull,
                          stderr=devnull)

    # Создание ссылки
    subprocess.check_call(["ln", "-snf", "/run/systemd/resolve/resolv.conf",
                          "/etc/resolv.conf"],
                          stdout=devnull,
                          stderr=devnull)

    # Запуск systemd-resolved / автозагрузка
    subprocess.check_call(["systemctl", "enable", "--now",
                          "systemd-resolved.service"],
                          stdout=devnull,
                          stderr=devnull)
    #########################
    write_wireless()

    #######################
    # Перезапуск службы
    subprocess.check_call(
                        ["systemctl", "restart", "systemd-networkd"],
                        stdout=devnull,
                        stderr=devnull
                        )
    #################################################################
    # ALPHA версия

    profiles = profiles_mkdir()
    c = Counter(profiles)
    profiles = list(set([line if c[line] == 1 else line + f" ({c[line]}x)"
                        for line in profiles]))
    profiles.append("Добавить профиль")
    profile = None

    if len(profiles) >= 1:  # Если, найдено больше одного профиля:
        profile = input_list(
                            "Найдено больше одного профиля, "
                            "какой желаете запустить?",
                            profiles,
                            color="yellow")
        if profile.endswith('x)'):
            profile = profile[:-6]

        if profile != "Добавить профиль":
            name_wifi = "wpa_supplicant-{}-{}.conf".format(profile,
                                                           device_user)
            path = f"/etc/wpa_supplicant/{name_wifi}"
            ssid = profile
            path = correct_Profile(profile)
            password = view_password(path)

    if (len(profiles) == 0 or
            profile == "Добавить профиль"):

        # Или в случае, если выбран 'добавить профиль':
        # Или профилей вообще нет

        ssid, password = password_and_ssid()
        # Создание профиля
    status_write = write_profile(ssid, password)
    if status_write is True:
        print_arr("Профиль был успешно создан!", color="green")
        path = write_profile.__annotations__["path"]
        device = write_profile.__annotations__["device"]

    else:  # В случае, если профиль выбран
        user_choice_input = input_y_n("Профиль существует, перезаписать?"
                                      " (y, n)", color="yellow")
        if user_choice_input == 1:
            password = password_user(ssid)
            write_profile(ssid, password, replace=True)
            print_arr("Перезаписано!", color="green")
            device = write_profile.__annotations__["device"]
            path = write_profile.__annotations__["path"]
        if user_choice_input == 0:
            path = status_write
        #
        #################################################################
    check_status = check_connect(timeout=0, print_output=False)
    if check_status == 1:
        ppid_user = ppid()
        kill_internet(ppid_user, print_output=False)

    os.popen("systemctl stop wpa_supplicant_python.service")

    status_connect = connect(device_user, path)

    if status_connect == 0:
        print_arr("device - ", device_user, color="yellow")
        print_arr("path - ", path, color="yellow")

    if status_connect == 1:
        status_daemon = write_daemon(device=device_user, path=path)

except (KeyboardInterrupt, EOFError):
    print()
    print_arr("Остановлено!", color="red")
    raise SystemExit(1)
