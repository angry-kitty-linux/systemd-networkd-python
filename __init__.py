#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Проверка на существование psutil / Аргументы"""

class PsutilNotFound(Exception): pass

import argparse

try:
    import psutil
except ModuleNotFoundError:
    raise PsutilNotFound("Похоже, psutil не установлен")


parser = argparse.ArgumentParser(prog="wpa-supplicant-python",
                                 description='Настройка wpa-supplicant.',
                                 add_help=False)

group = parser.add_argument_group("Options")
group.add_argument("-h", "--help", action="help", help="Показать справку")
group.add_argument('--device',
                   action="store",
                   metavar="<device>",
                   default=False,
                   help="Ввод используемого модуля")
args = parser.parse_args()
