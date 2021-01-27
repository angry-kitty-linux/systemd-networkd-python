#!/usr/bin/python

import os
import getpass
from colors import print_arr
from writes import *
from connection import connect
from connection import check_connect
from connection import kill
from connection import ppid
from connection import kill_internet

try:
    user = getpass.getuser() # Узнаем пользователя

    if user != "root":
        print_arr(f"Привет,", user, color = "green")
        print_arr("Для работоспособности программы Вам требуется root", color = "red")
        exit()
    
    check_status = check_connect(timeout = 0, print_output = False)

    if check_status == 1:
        ppid = ppid()
        if ppid != None:
            print_arr("Обнаружено соединение с использование wpa_supplicant, прервать? (y, n)", color = "yellow")
            
            kill_internet(ppid)

    bool_path = os.path.exists(path_dhcp)
    
    if bool_path is True:
        print_arr("Обнаружена существующая конфигурация, перезаписать? (y, n)", color = "yellow")
        
        while True:
            user_choice = input("> ")

            if "y" in user_choice: 
                print_arr("Удаляю конфиг...", color = "green")
                os.remove(path_dhcp)
                print_arr("Записываю конфиг...", color = "green")
                write_dhcp()
                break

            if "n" in user_choice:
                print_arr("OK, оставляю на месте!", color = "green")
                break

            else:
                print_arr("Не понимаю о чем Вы, повторите еще раз...", color = "red")
    
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
        print_arr("Желаете перезаписать? (y, n)", color = "yellow")
        
        while True:
            user_choice = input("> ")

            if "y" in user_choice:
                os.remove(path_wireless)
                write_wireless() 
                break

            if "n" in user_choice:
                break 
            
            else:
                print_arr("Не понимаю о чем Вы, повторите еще раз...", color = "red")
    
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
        print_arr("Профиль существует, перезаписать? (y, n)", color = "yellow")
        
        while True:
            user_choice = input("> ")
        
            if "y" in user_choice:
                write_profile(ssid, password, replace = True)
                print_arr("Перезаписано!", color = "green")
                device = write_profile.__annotations__["device"]
                path = write_profile.__annotations__["path"]
                
                break

            if "n" in user_choice:
                print_arr("OK.", color = "green")
                profiles_dir = os.listdir("/etc/wpa_supplicant")
                print_arr(profiles_dir, color = "red")
                if len(profiles_dir) > 1:
                    profiles_supl = [line.replace("wpa_supplicant-", "")[:-5] for line in profiles_dir]
                    profiles = [line[:line.rfind("-")] for line in profiles_supl]
                    print_arr("Найдено больше одного профиля, какой желаете запустить?", color = "yellow")
                    
                    print()
                    print_arr("-" * 25, color = "green")
                    for ind, value in enumerate(profiles, 1):
                        print_arr(f"[{ind}] ", value, color = "red")
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
                            break

                        except ValueError as e:
                            print (e)
                            if str(user_choice) not in profiles:                   
                                print_arr(f"{user_choice} не существует!", color = "red")
                            
                            else: 
                                name_wifi = [line for line in profiles_supl if user_choice in line]
                                if len(name_wifi) > 1:
                                    print_arr("Ошибка! Обнаружено несколько одинаковых профилей!", color = "red")
                                    exit()

                                if len(name_wifi) == 1:   # Знаю, есть else, но не хочу делать нечитаемым код
                                    index = name_wifi[0].rfind("-")
                                    device = name_wifi[0][index:]
                                    name_wifi = "wpa_supplicant-{}.conf".format(name_wifi[0])
                                    path = f"/etc/wpa_supplicant/{name_wifi}"
                                break
                
                if len(profiles_dir) == 1:
                    index = slice(14, -5)
                    print_arr("Обнаружен единственный профиль. Подключаю...", color = "green")
                    path = f"/etc/wpa_supplicant/{profiles_dir[0]}"
                    device = profiles_dir[0][index]
                    print (device)
                    device = device[device.rfind("-") + 1:]
                break

            else:
                print_arr("Не понимаю о чем Вы, повторите еще раз...", color = "red")

    status_connect = connect(device, path)

    if status_connect == 0:
        print_arr ("device - ", device, color = "yellow")
        print_arr("path - ", path, color = "yellow")
except KeyboardInterrupt:
    print ()
    print_arr("Остановлено!", color = "red")
