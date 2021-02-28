#!/usr/bin/python
# -*- coding: utf-8 -*-

from colors import print_arr

"""
Тут я буду по возможности создавать декораторы для разных целей
"""

def KeyboardError():
    """ Обработка CTRL + C """

    def wrap(func):
        def wrap2(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (KeyboardInterrupt, EOFError):
                print()
                print_arr("Остановлено!", color = "red")
                exit()
        return wrap2
    return wrap


def Check_error():
    """ Обработка состояние функции """
    def wrap(func):
        def wrap2(*args, **kwargs):
            try:
                return_status =  func(*args, **kwargs)
            except Exception as e:
                print_arr ("Произошла ошибка!", color = "red")
                print_arr(e, color = "red")

                return 0
            else:
                if return_status is None: return 1
                if return_status is not None: return return_status
        return wrap2
    return wrap

