#!/usr/bin/python

import os
from colors import print_arr
from wrappers import KeyboardError

@KeyboardError()
def input_y_n(text: str, color: str):
    
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

@KeyboardError()
def input_list(text_quest:str, text: list[str], color: str) -> int:
    
    text_quest: "Вопрос"
    text: "Варианты ответов"

    assert type(text) is list
    
    print_arr(text_quest, color = color)
    
    print()
    print_arr("-" * 25, color = "green")
    for ind, value in enumerate(text, 1):
        print_arr(f"[{ind}] ", value, color = "red", arrow = False)
    print_arr("-" * 25, color = "green")

    while True:
        try:
            user_choice = input("> ").lower()
            
            if len(user_choice) > 3 or int(user_choice) <= 0 or int(user_choice) > ind:
                raise ValueError
            
            else:
                return int(user_choice)
        
        except ValueError:
            print_arr(f"{user_choice} не существует!", color = "red")
