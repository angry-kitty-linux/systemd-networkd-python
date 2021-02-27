#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from colors import print_arr
from input_while import input_y_n 
import subprocess


from config import devnull

def auto_wpa(print_output = True) -> int:

    print_output: "Вывод"

    try:
        if print_output:
            print_arr("Добавляю в автозагрузку...", color = "green")

        subprocess.check_call(["systemctl", "enable", "wpa_supplicant_python.service"], stdout = devnull,
                                                                                        stderr = devnull)
        return 1
    except subprocess.CalledProcessError as e:
        print_arr(e, color = "red")
        return 0

def write_daemon(device:str, path:str) -> int:
    device: "Модуль вайли"
    path: "Путь до конфига"

    daemon = f"""
[Unit]
Description = wpa_supplicant_python запущен!
After = network.target
[Service]
ExecStart = /usr/bin/wpa_supplicant -B -i {device} -c {path}
RemainAfterExit=true
[Install]
WantedBy = multi-user.target
"""

    path_daemon = "/etc/systemd/system/wpa_supplicant_python.service"

    if os.path.exists(path_daemon):
        user_choice = input_y_n("Обнаружен существующий демон. Перезаписать? (y, n)", color = "yellow")
        
        if user_choice == 1:
            os.remove(path_daemon)
            with open(path_daemon, "w") as f:
                f.write(daemon)
            
            return 1
    else:
        user_choice = input_y_n("Желаете добавить в автозагрузку? (y, n)", color = "yellow")
        
        if user_choice == 1:
            with open(path_daemon, "w") as f:
                f.write(daemon)

            if auto_wpa(print_output = False) != 1:
                print_arr("Не удалось добавить в автозагрузку!", color = "red")
                exit()


