#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

"""
Это файл, в котором хранятся все пути, для сохранения профилей. 
И не только
"""

devnull = open(os.devnull, "wb")

path_dhcp = "/etc/systemd/network/50-dhcp.network"
path_wireless = "/etc/systemd/network/25-wireless.network" 

