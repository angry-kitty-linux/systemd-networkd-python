#!/usr/bin/python

""" Проверка на существование psutil """

class PsutilNotFound(Exception): pass


try:
    import psutil
except ModuleNotFoundError: 
    raise PsutilNotFound("Похоже, psutil не установлен")
