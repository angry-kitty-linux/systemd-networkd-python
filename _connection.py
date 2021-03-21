#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Взаимодействие с соединением.
Здесь будет происходить подключение,
проверка соединение и т.д
"""

import os
from _colors import print_arr
from _daemon import write_daemon
import subprocess
import time
from typing import Union
from typing import List
import _writes
import _input_while

from _config import path_dhcp
from _config import path_wireless
from _config import devnull

from _wrappers import Check_error


@Check_error()
def check_connect(timeout: int = 10, print_output: bool = True) -> int:
    """ Проверка соединения с интернетом """

    # timeout - "Задержка (wpa_supplicant не сразу включается)"
    # print_output - "Печатать вывод"

    try:
        if print_output is True:
            print_arr("Проверка соединения...", color="yellow")

        time.sleep(timeout)

        subprocess.check_call(["ping", "-c 1", "eth0.me"],
                              stdout=devnull,
                              stderr=devnull
                              )
        return 1
    except subprocess.CalledProcessError:
        return 0


@Check_error()
def connect(device: str, path: str, print_output: bool = True) -> int:
    """ Используется для подключение к интернету """

    # device "Модуль вафли"
    # path "Путь до конфига"
    # print_output "Печатать вывод"

    _writes.extra_kill()
    # Финальный шаг
    command = "wpa_supplicant -B -i {} -c {}".format(device, path)
    output = os.popen(command).read()
    connect.__annotations__['output'] = output

    if check_connect() == 1:
        if print_output is True:
            print_arr("Подключено!", color="green")
        return 1

    else:
        if print_output is True:
            print_arr(output, color="red")
            print_arr("Не получилось подключится ): ", color="red")
        return 0


@Check_error()
def kill_internet(ppid: int, print_output: bool = True) -> int:
    """ Отключение от интернета """

    # print_output "Печать вывода"
    # ppid "Номер процесса"

    if print_output is True:
        status_user = _input_while.input_y_n("Обнаружено соединение с ",
                                            "использованием wpa_supplicant,"
                                            " прервать? (y, n)",
                                            color="yellow")
        if status_user == 1:
            subprocess.check_call(
                                ["systemctl", "stop", "wpa_supplicant_python.service"],
                                stdout=devnull,
                                stderr=devnull
                                )

            # Пробуем остановить службу (если её нет, то ничего не произойдет)
            _writes.kill(ppid)
            print_arr("Соединение было разорвано!", color="red")
            return 1

        if status_user == 0:
            if print_output is True:
                print_arr("Учтите, т.к wpa_supplicant запущен,",
                          "могут возникнуть проблемы", color="red")
            return 0

    if print_output is False:
        subprocess.check_call(
                            ["systemctl", "stop", "wpa_supplicant_python.service"],
                            stdout=devnull,
                            stderr=devnull
                            )
        _writes.kill(ppid)
        return 1


@Check_error()
def watch_ssid() -> Union[int, List[str]]:
    """
    Функция для просмотра SSID
    """

    try:
        out = os.popen("wpa_cli scan").read().split("\n")
        if "OK" in out[1]:
            print_arr("Идет поиск WI-FI сетей...", color="yellow")

            time.sleep(2)

            wifi_list = os.popen("wpa_cli scan_results").read()
            wifi_list = wifi_list.split("\n")
            wifi_list_dirty = wifi_list[2:]
            wifi_list_dirty = [[line.replace('\t', " ")] for line in wifi_list_dirty]

            wifi_list_clean = []
            for line in wifi_list_dirty:
                wifi_list_clean.append([element.split(" ") for element in line])

            del wifi_list_clean[-1]

            print (print_arr("MAC", color="pink",
                             return_color=True).rjust(26),end="")

            print (print_arr("SIGNAL", color="pink",
                             return_color=True).rjust(22), end="")

            print (print_arr("SECURITY", color="pink",
                             return_color=True).center(23), end="")

            print (print_arr("SSID", color="pink",
                             return_color=True).center(34), end="")
            print()

            unpack = lambda *x: x
            counter = 0
            ssids_wifi = []
            for line in wifi_list_clean:
                for line2 in line:
                    if len(line2) != 5:
                        for number, string in enumerate(line2, 0):
                            if string.rfind("[ESS]") == -1: continue
                            else:
                                break

                        ssid_full = ""
                        for last_word in line2[number + 1:]:
                            ssid_full += last_word

                        del line2[number + 1:]
                        line2.append(ssid_full)

                    for mac, none, signal, security, ssid in unpack(line2):
                        counter += 1

                        ssids_wifi.append(ssid)
                        counter_text = f"[{counter}]"

                        signal = int(signal[1:])
                        #######################################################
                        # MAC Адресс
                        text = print_arr(mac, color="yellow", arrow=False,
                                         return_color=True).ljust(len(mac) + 10, "|")
                        text = "{0}{2}\033[39m|\033[39m{1}".format(counter_text.center(6), text, "")
                        print (text, end="")
                        #######################################################

                        # Уровень сигнала

                        ##########
                        # Покраска текста
                        if signal < 65: color = "green"
                        elif signal < 75: color = "yellow"
                        elif signal < 85: color = "red"
                        else: color = "red"
                        ##########

                        text = print_arr(
                                        signal,
                                        color=color,
                                        return_color=True
                                        ).ljust(12)

                        print (f"  {text} |", end = "")
                        #######################################################

                        # Безопасность

                        if security == "[ESS]":
                            text = "None".center(8)
                        elif "[WPA-PSK-CCMP+TKIP]" in security or "[WPA2-PSK-CCMP+TKIP]" in security:
                            text = "WPA/WPA2"

                        elif "[WPA-PSK-CCMP]" in security or "[WPA2-PSK-CCMP]"in security:
                            text = "WPA/WPA2"


                        text = print_arr(text, color="red", return_color=True).ljust(12)
                        print(f" {text} ".ljust(20, "|"), end="")
                        #######################################################

                        # SSID сетей
                        text = print_arr(ssid, color="blue", return_color=True).center(35)
                        if ssid == "":
                            text = print_arr("<SSID не обнаружен!>", color="red", return_color=True).center(35)

                        print (f"{text}".ljust(len(text) + 1, "|"))
            print()
            return ssids_wifi

        else:
            print(out)
            print_arr (out[1], color="red")
            print_arr("Не удалось просканировать сети!", color="red")

    except Exception:
        return 0


def scan():
    """ Сканирование точек """

    subprocess.check_call(
                        ["wpa_cli", "scan"],
                        stdout=devnull,
                        stderr=devnull
                        )


def info_ssid():
    """ Получение информации о точках доступа """

    scan()
    time.sleep(2.500)

    wifi_list = os.popen("wpa_cli scan_results").read()
    wifi_list = wifi_list.split("\n")
    wifi_list_dirty = wifi_list[2:]
    wifi_list_dirty = [[line.replace('\t', " ")] for line in wifi_list_dirty]

    if len(wifi_list_dirty) == 1:
        scan()
        time.sleep(1)
        wifi_list = os.popen("wpa_cli scan_results").read()
        wifi_list = wifi_list.split("\n")
        wifi_list_dirty = wifi_list[2:]
        wifi_list_dirty = [[line.replace('\t', " ")] for line in wifi_list_dirty]

    wifi_list_clean = []

    for line in wifi_list_dirty:
        wifi_list_clean.append([element.split(" ") for element in line])

    del wifi_list_clean[-1]

    list_ssid = []
    for line in wifi_list_clean:
        for line2 in line:
            if line2[-1] != '':
                list_ssid.append(line2[-1])

    return list_ssid
