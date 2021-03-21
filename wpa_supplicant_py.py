#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Основной файл """


import os
import subprocess
from _colors import print_arr

from _writes import write_dhcp, write_wireless, write_profile
from _writes import status_function
from _writes import check_root
from _writes import ppid
from _writes import russian_locale
from _writes import module_profile
from _writes import password_and_ssid
from _writes import profiles_mkdir
from _writes import view_password

from _connection import connect
from _connection import check_connect
from _connection import kill_internet
from _connection import watch_ssid

from _daemon import write_daemon

from _input_while import input_y_n
from _input_while import input_list
from _input_while import password_user

from _config import path_dhcp
from _config import path_wireless
from _config import devnull


try:

    russian_locale()
    check_root()
    device_user = status_function()
    # -----------------------

    module_profile()
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

    profiles = profiles_mkdir()
    profiles.append("Добавить профиль")
    profile = None

    user_choice = input_y_n(
                            "Желаете отобразить все доступные WI-FI сети?"
                            " (Может не работать)",
                            color="green"
                            )

    assert_error = False
    if user_choice == 1:
        ssids = watch_ssid()

        try:
            ssid = input_list(
                            "Выберите нужный SSID:",
                            ssids,
                            color="yellow",
                            print_output=False)

            password = password_user(ssid)

        except AssertionError:    # В случае, если SSID не удалось просканировать
            assert_error = True

        else:
            assert_error = False

    if user_choice == 0:  # Если не отображать доступные сети:
        if len(profiles) >= 1:  # Если, найдено больше одного профиля:
            profile = input_list(
                                "Найдено больше одного профиля, "
                                "какой желаете запустить?",
                                profiles,
                                color="yellow")

            ssid = profile
            password = view_password("/etc/wpa_supplicant/wpa_supplicant-{}-"
                                     "{}.conf".format(profile, device_user))
            if len(profiles) != profile:
                name_wifi = "wpa_supplicant-{}-{}.conf".format(profile, device_user)
                path = f"/etc/wpa_supplicant/{name_wifi}"

    if (len(profiles) == 0
        or len(profiles) == profile
        or assert_error is True):

        # Или в случае, если выбран 'добавить профиль':
        # Или профилей вообще нет

        ssid, password = password_and_ssid()

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

    subprocess.check_call(
                        ["systemctl", "stop", "wpa_supplicant_python.service"],
                        stdout=devnull,
                        stderr=devnull
    )

    status_connect = connect(device_user, path)

    if status_connect == 0:
        print_arr("device - ", device_user, color="yellow")
        print_arr("path - ", path, color="yellow")

    if status_connect == 1:
        status_daemon = write_daemon(device=device_user, path=path)

except (KeyboardInterrupt, EOFError):
    print()
    print_arr("Остановлено!", color="red")
