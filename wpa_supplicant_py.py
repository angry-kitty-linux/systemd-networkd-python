#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess

from colors import print_arr

from writes import write_dhcp
from writes import write_wireless
from writes import write_profile
from writes import status_function
from writes import check_root
from writes import kill
from writes import ppid
from writes import russian_locale
from writes import default_locale

from connection import connect
from connection import check_connect
from connection import kill_internet
from connection import watch_ssid
from connection import info_ssid

from daemon import write_daemon
from daemon import auto_wpa

from input_while import input_y_n
from input_while import input_list
from input_while import password
from input_while import ssid

from config import path_dhcp
from config import path_wireless
from config import devnull

try:

    russian_locale()
    check_root()
    status_function()

    # -----------------------

    check_status = check_connect(
                                timeout=0,
                                print_output=False
                                )

    if check_status == 1:
        ppid_wpa = ppid()
        if ppid_wpa is not None:
            kill_internet(ppid_wpa)

        if ppid_wpa is None:
            print_arr("Обнаружено соединение с использованием неизвестного ПО", color="red")
            print_arr("Пожалуйста, выключите сервисы, предостовляющие интернет соединение!", color="red")
            exit()

    bool_path = os.path.exists(path_dhcp)

    if bool_path is True:
        user_choice = input_y_n("Обнаружена существующая конфигурация, перезаписать? (y, n)", color="yellow")

        if user_choice == 1:
            print_arr("Записываю конфиг...", color="green")
            write_dhcp()

        if user_choice == 0:
            print_arr("OK, оставляю на месте!", color="green")

    if bool_path is False:
        print_arr("Конфигурация не найдена, создаю новый конфиг...", color="yellow")
        write_dhcp()

    #########################
    # Добавление в автозагрузку
    print_arr("Запускаю/добавляю в автозагрузку systemd-networkd...", color="green")
    subprocess.check_call(
                        ["systemctl", "enable", "--now", "systemd-networkd.service"],
                        stdout=devnull,
                        stderr=devnull
                        )
    # Создание ссылки
    subprocess.check_call(
                          ["ln", "-snf", "/run/systemd/resolve/resolv.conf", "/etc/resolv.conf"],
                          stdout=devnull,
                          stderr=devnull
                         )

    # Запуск systemd-resolved / автозагрузка
    subprocess.check_call(
                          ["systemctl", "enable", "--now", "systemd-resolved.service"],
                          stdout=devnull,
                          stderr=devnull
                         )
    #########################

    # Проверка на существование ..../25-wireless.network
    bool_path = os.path.exists(path_wireless)

    if bool_path is True:
        print_arr("Обнаружен 25-wireless.network()", color="yellow")
        user_choice = input_y_n("Желаете перезаписать? (y, n)", color="yellow")

        if user_choice == 1:
            print_arr("OK.", color="green")
            write_wireless(replace=True)

    if bool_path is False:
        print_arr("Конфигурация была не найдена! Создаю...", color="yellow")
        write_wireless()

    #######################
    # Перезапуск службы
    subprocess.check_call(
                        ["systemctl", "restart", "systemd-networkd"],
                        stdout=devnull,
                        stderr=devnull
                        )
    #####

    #################################################################
    # ALPHA версия
    """
    user_choice = input_y_n(
                            "Желаете отобразить все доступные WI-FI сети?",
                            color="green"
                            )
    if user_choice == 1:
        ssids = watch_ssid()
        ssid = input_list("Выберите нужный SSID:",
                            ssids, color="yellow",
                            print_output=False
                        )

        ssid = ssids[ssid - 1]
    """
    profiles_dir = os.listdir("/etc/wpa_supplicant")

    profile = None
    if len(profiles_dir) >= 1:  # Если, найдено больше одного профиля:
        profiles_supl = [line.replace("wpa_supplicant-", "")[:-5] for line in profiles_dir]
        profiles = [line[:line.rfind("-")] for line in profiles_supl]
        profiles.append("Добавить профиль")

        profile = input_list("Найдено больше одного профиля, какой желаете запустить?",
                    profiles, color="yellow")

        if len(profiles) != profile:
            name_wifi = profiles_supl[profile - 1]
            device = name_wifi[name_wifi.rfind("-") + 1:]
            name_wifi = "wpa_supplicant-{}.conf".format(name_wifi)
            path = f"/etc/wpa_supplicant/{name_wifi}"

    if len(profiles_dir) == 0 or len(profiles) == profile:
        # Или в случае, если выбран 'добавить профиль':
        # Или профилей вообще нет

        # Ввод ssid
        print_arr("Введите SSID (название точки доступа)", color="green")
        ssid_user = input("> ")
        # Ввод пароля
        password = password(ssid_user)

        # Создание профиля
        if write_profile(ssid, password):
            print_arr("Профиль был успешно создан!", color="green")
            path = write_profile.__annotations__["path"]
            device = write_profile.__annotations__["device"]

        else:  # В случае, если профиль выбран
            user_choice_input = input_y_n("Профиль существует, перезаписать? (y, n)", color="yellow")
            if user_choice_input == 1:
                write_profile(ssid, password, replace=True)
                print_arr("Перезаписано!", color="green")
                device = write_profile.__annotations__["device"]
                path = write_profile.__annotations__["path"]
    #
    #################################################################


    check_status = check_connect(timeout=0, print_output=False)
    if check_status == 1:
        ppid_user = ppid()
        kill_internet(ppid_user, print_output=False)

    status_connect = connect(device, path)

    if status_connect == 0:
        print_arr("device - ", device, color="yellow")
        print_arr("path - ", path, color="yellow")

    if status_connect == 1:
        status_daemon = write_daemon(device=device, path=path)

except (KeyboardInterrupt, EOFError):
    print()
    print_arr("Остановлено!", color="red")
