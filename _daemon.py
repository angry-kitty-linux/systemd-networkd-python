#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Для работы/создания демона """


import subprocess
import os

from _colors import print_arr

from _config import devnull
from _config import path_daemon

from _wrappers import Check_error

import _input_while


@Check_error()
def auto_wpa(print_output: bool = True) -> int:
    """ Добавляем наш демон в автозагрузку """

    # print_output "Вывод"

    try:
        if print_output:
            print_arr("Добавляю в автозагрузку...", color="green")

        subprocess.check_call(["systemctl", "enable",
                              "wpa_supplicant_python.service"],
                              stdout=devnull,
                              stderr=devnull)
        return 1
    except subprocess.CalledProcessError as error:
        print_arr(error, color="red")
        return 0


@Check_error()
def write_daemon(device: str, path: str) -> int:
    """ Создаём демона """

    # device "Модуль вайли"
    # path "Путь до конфига"

    daemon = f"""
[Unit]
Description = network connection
After = network.target
[Service]
ExecStart = /usr/bin/wpa_supplicant -B -i {device} -c {path}
RemainAfterExit=true
[Install]
WantedBy = multi-user.target
"""
    if os.path.exists(path_daemon):
        with open(path_daemon) as file:
            if file.read() == daemon:
                raise SystemExit(0)

        user_choice = _input_while.input_y_n("Обнаружен существующий демон.",
                                             " Перезаписать? (y, n)",
                                             color="yellow")

        if user_choice == 1:
            os.remove(path_daemon)
            with open(path_daemon, "w") as file:
                file.write(daemon)

            return 1
    else:
        user_choice = _input_while.input_y_n("Желаете добавить в автозагрузку"
                                             "? (y, n)",
                                             color="yellow")

        if user_choice == 1:
            with open(path_daemon, "w") as file:
                file.write(daemon)

            if auto_wpa(print_output=False) != 1:
                print_arr("Не удалось добавить в автозагрузку!", color="red")
                raise SystemExit(0)
