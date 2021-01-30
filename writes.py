#!/usr/bin/python

import psutil
import os

path_dhcp = "/etc/systemd/network/50-dhcp.network"
path_wireless = "/etc/systemd/network/25-wireless.network"

devices = [line for line in psutil.net_if_stats()]
device_list = [line for line in devices if line != 'lo']

if len(device_list) == 1:
    device = device_list[0]

def write_dhcp(): # Функция, для создания конфига в systemd-networkd  
    with open(path_dhcp, 'w') as f:
        f.write("""
[Match]
Name=en*
 
[Network]
DHCP=yes
""")



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
        
        print (device)
        return True


