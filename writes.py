#!/usr/bin/python

import getpass
from colors import print_arr
from input_while import input_y_n
import os
from connection import check_connect
from typing import Union
import subprocess
import re


path_dhcp = "/etc/systemd/network/50-dhcp.network"
path_wireless = "/etc/systemd/network/25-wireless.network"

devnull = open(os.devnull, "wb")

def check_root():
    user = getpass.getuser() # Узнаем пользователя

    if user != "root":
        print_arr(f"Привет, ", user, color = "green")
        print_arr("Для работоспособности программы Вам требуется root", color = "red")
        exit()

def device():

    global device

    devices = [line for line in psutil.net_if_stats()]
    device_list = [line for line in devices if line != 'lo']

    if len(device_list) == 1:
        device = device_list[0]
    else:
        print_arr(text = "Обнаружено несколько модулей WI-FI, выберите нужный!", color = "yellow")

def write_dhcp(): # Функция, для создания конфига в systemd-networkd  
    with open(path_dhcp, 'w') as f:
        f.write("""
[Match]
Name=en*
 
[Network]
DHCP=yes
        """)

def status_function():
    global psutil

    """
    Функция для того, чтобы сообщить всем остальным использовать локальную версию
    """

    try:
        import psutil
    except ModuleNotFoundError:
        print_arr("Psutil не найден в системе!", color = "red")
        status_choice = input_y_n("Желаете использовать pip, для установки? (y, n)", color = "yellow")
        if status_choice == 1:
            if check_connect(timeout = 0, print_output = False):
                try:
                    subprocess.check_call(["pip", "install", "psutil"])
                    import psutil
                except FileNotFoundError:
                    print_arr("У вас не установлен pip. Устанавливаю...", color = "green")
                    subprocess.check_call(["curl", "https://bootstrap.pypa.io/get-pip.py", "-o", "get-pip.py"], stdout=devnull, stderr=devnull)
                    subprocess.check_call(["python", "get-pip.py"], stderr = devnull, stdout = devnull)
                    subprocess.check_call(["pip", "install", "psutil"], stdout = devnull, stderr = devnull)
                    print_arr("Psutil установлен!", color = "green")
                    os.remove("get-pip.py")

                    import psutil
            else:
                print_arr("Отсутсвует соединение с интернетом. Использую локальную версию...", color = "yellow")
                import psutil_loc as psutil
    device()



def write_wireless():
    with open(path_wireless, "w") as f:
        f.write(f"""
[Match]
Name={device}
[Network]
DHCP=ipv4
""")

def write_profile(ssid:str, password:str, replace = False) -> bool:
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
        write_profile.__annotations__["device"] = device
        write_profile.__annotations__["path"] = path
        
        return True


def ppid() -> int:
    for proc in psutil.pids():
        p = psutil.Process(proc)
        if 'wpa_supplicant' == str(p.name()):
            return p.pid

def check_service() -> int:
    known_cgroups = set()
    for pid in psutil.pids():
        try:
            cgroups = open('/proc/%d/cgroup' % pid, 'r').read()
        except IOError:
            continue
        systemd_name_match = re.search('^1:name=systemd:(/.+)$', cgroups, re.MULTILINE)
        if systemd_name_match is None:
            continue
        systemd_name = systemd_name_match.group(1)
        if systemd_name in known_cgroups:
            continue 
        if not systemd_name.endswith('.service'):
            continue 
        known_cgroups.add(systemd_name)

        if "wpa_supplicant_python.service" in systemd_name:
            return 1
        else:
            return 0


def kill(id_proccess: int) -> int:
    id_proccess: "Айди процесса, для убийства"
    try:
        
        if check_service() == 1:
            subprocess.check_call(["systemctl", "stop", "wpa_supplicant_python.service"], 
                                    stderr = devnull, stdout = devnull)
        
        process = psutil.Process(id_proccess)
        process.kill()

        return 1
    except:
        return 0

def default_locale() -> int:
    
    """
    Функция для установки дефолтного шрифта
    """

    subprocess.check_call(["setfont"])

def check_locale() -> int:
    with open("/etc/locale.gen", "r") as f:
        if "#ru_RU.UTF-8 UTF-8" in f.read():
            return 1
        else:
            return 0
    
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
                print(file_read, file = f)

            subprocess.check_call(["locale-gen"])
        
        subprocess.check_call(["setfont", "latarcyrheb-sun16"], stderr=devnull)

        return 1
    except (FileNotFoundError, subprocess.CalledProcessError) :
        return 0 

