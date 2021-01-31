#!/usr/bin/python

import os
import getpass
from colors import print_arr
from writes import write_dhcp 
from writes import write_wireless
from writes import write_profile
from writes import status_function
from connection import connect
from connection import check_connect
from writes import kill
from writes import ppid
from connection import kill_internet
from daemon import write_daemon
from daemon import auto_wpa
from input_while import input_y_n

try:
    
    user = getpass.getuser() # Узнаем пользователя

    if user != "root":
        print_arr(f"Привет, ", user, color = "green")
        print_arr("Для работоспособности программы Вам требуется root", color = "red")
        exit()
    
    check_status = check_connect(timeout = 0, print_output = False)

    if check_status == 1:
        ppid_wpa = ppid()
        if ppid_wpa != None:
            print_arr("Обнаружено соединение с использование wpa_supplicant, прервать? (y, n)", color = "yellow")
            
            kill_internet(ppid_wpa)

    bool_path = os.path.exists(path_dhcp)
    
    if bool_path is True:
        user_choice = input_y_n("Обнаружена существующая конфигурация, перезаписать? (y, n)", color = "yellow") 

        if user_choice == 1: 
            print_arr("Удаляю конфиг...", color = "green")
            os.remove(path_dhcp)
            print_arr("Записываю конфиг...", color = "green")
            write_dhcp()

        if user_choice == 0:
            print_arr("OK, оставляю на месте!", color = "green")
    
    if bool_path is False:
        print_arr("Конфигурация не найдена, создаю новый конфиг...", color = "yellow")
        write_dhcp()
    
    #########################
    # Добавление в автозагрузку
    print_arr("Запускаю/добавляю в автозагрузку systemd-networkd...", color = "green")
    os.system("systemctl enable --now systemd-networkd.service")
    # Создание ссылки
    os.system("ln -snf /run/systemd/resolve/resolv.conf /etc/resolv.conf")
    # Запуск systemd-resolved / автозагрузка
    os.system("systemctl enable --now systemd-resolved.service")
    #########################

    # Проверка на существование ..../25-wireless.network
    bool_path = os.path.exists(path_wireless)
    
    if bool_path is True:
        print_arr("Обнаружен 25-wireless.network()", color = "yellow")

        user_choice = input_y_n("Желаете перезаписать? (y, n)", color = "yellow")

        if user_choice == 1:
            os.remove(path_wireless)
            write_wireless() 

    if bool_path is False:
        print_arr("Конфигурация была не найдена! Создаю...", color = "yellow")
        write_wireless()
    
    ####################### 
    # Перезапуск службы
    os.system("systemctl restart systemd-networkd")
    #####

    print_arr("Теперь введите SSID (название точки доступа)", color = "green")
    ssid = input("> ")
    print_arr(f"Введите пароль от {ssid}", color = "green")
    password = input("> ")
    
    # Создание профиля
    if write_profile(ssid, password):
        print_arr("Профиль был успешно создан!", color = "green") 
        path = write_profile.__annotations__["path"]
        device = write_profile.__annotations__["device"]
    
    else:
        user_choice = input_y_n("Профиль существует, перезаписать? (y, n)", color = "yellow")
        
        if user_choice == 1:
            write_profile(ssid, password, replace = True)
            print_arr("Перезаписано!", color = "green")
            device = write_profile.__annotations__["device"]
            path = write_profile.__annotations__["path"]
                
        if user_choice == 0:
            print_arr("OK.", color = "green")
            profiles_dir = os.listdir("/etc/wpa_supplicant")
            if len(profiles_dir) > 1:
                profiles_supl = [line.replace("wpa_supplicant-", "")[:-5] for line in profiles_dir]
                profiles = [line[:line.rfind("-")] for line in profiles_supl]
                print_arr("Найдено больше одного профиля, какой желаете запустить?", color = "yellow")
                    
                print()
                print_arr("-" * 25, color = "green")
                for ind, value in enumerate(profiles, 1):
                    print_arr(f"[{ind}] ", value, color = "red", arrow = False)
                print_arr("-" * 25, color = "green")

                while True:
                    try:
                        user_choice = input("> ")
                        user_choice = int(user_choice)
                            
                        if user_choice < 1 or user_choice > ind and len(str(user_choice)) < 3:
                            print_arr(f"{user_choice} не существует!", color = "red")
                            
                        else:
                            name_wifi = profiles_supl[user_choice - 1]
                            name_wifi = "wpa_supplicant-{}.conf".format(name_wifi)
                            path = f"/etc/wpa_supplicant/{name_wifi}"
                            break

                    except ValueError as e:
                        if str(user_choice) not in profiles:                   
                            print_arr(f"{user_choice} не существует!", color = "red")
                            
                        else: 
                            name_wifi = [line for line in profiles_supl if user_choice in line]
                            if len(name_wifi) > 1:
                                print_arr("Ошибка! Обнаружено несколько одинаковых профилей!", color = "red")
                                exit()

                            if len(name_wifi) == 1:   # Знаю, есть else, но не хочу делать нечитаемым код
                                index = name_wifi[0].rfind("-") + 1
                                device = name_wifi[0][index:]
                                name_wifi = "wpa_supplicant-{}.conf".format(name_wifi[0])
                                path = f"/etc/wpa_supplicant/{name_wifi}"
                            break
                
                if len(profiles_dir) == 1:
                    index = slice(14, -5)
                    print_arr("Обнаружен единственный профиль. Подключаю...", color = "green")
                    path = f"/etc/wpa_supplicant/{profiles_dir[0]}"
                    device = profiles_dir[0][index]
                    device = device[device.rfind("-") + 1:]

            else:
                print_arr("Не понимаю о чем Вы, повторите еще раз...", color = "red")

    check_status = check_connect(timeout = 0, print_output = False)
    if check_status == 1:
        ppid_user = ppid()
        kill(ppid_user)

    status_connect = connect(device, path)

    if status_connect == 0:
        print_arr ("device - ", device, color = "yellow")
        print_arr("path - ", path, color = "yellow")

    if status_connect == 1:
        status_daemon = write_daemon(device = device, path = path)    
        auto_wpa(print_output = True)    
        
except KeyboardInterrupt:
    print ()
    print_arr("Остановлено!", color = "red")
