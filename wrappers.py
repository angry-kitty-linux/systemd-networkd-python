#!/usr/bin/python

from colors import print_arr

def KeyboardError():
    def wrap(func):
        def wrap2(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (KeyboardInterrupt, EOFError):
                print()
                print_arr("Остановлено!", color = "red")
                default_locale()
                exit()
        return wrap2
    return wrap


