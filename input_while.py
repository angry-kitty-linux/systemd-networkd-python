#!/usr/bin/python

import os
from colors import print_arr

def input_y_n(text: str, color: str) -> int:
    
    text: "`text` будет появлятся при вопросе"

    print_arr(text, color = color)
    
    while True:
        user_choice = input("> ").lower()

        if user_choice == "y":
            return 1

        if user_choice == "n":
            return 0

        else:
            print_arr("Не понимаю о чем Вы, повторите еще раз...", color = "red")
