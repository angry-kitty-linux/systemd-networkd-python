#!/usr/bin/python
# -*- coding: utf-8 -*-

from _colors import print_arr
from _wrappers import KeyboardError
from typing import List
import _connection


@KeyboardError()
def input_y_n(*text: str, color: str):

    # text "`text` будет появлятся при вопросе"

    print_arr(*text, color=color)
    while True:
        user_choice = input("> ").lower()

        if user_choice == "y":
            return 1
        if user_choice == "n":
            return 0
        else:
            print_arr("Не понимаю о чем Вы, повторите еще раз...", color="red")


@KeyboardError()
def input_list(text_quest: str, text: List[str], color: str, print_output: bool = True) -> int:
    """ Менюшка с вариантами ответов """

    # text_quest "Вопрос"
    # text "Варианты ответов"

    assert isinstance(text, list)

    print_arr(text_quest, color=color)

    if print_output is True:
        print_arr("-" * 25, color="green")
        for ind, value in enumerate(text, 1):
            print_arr(f"[{ind}] ", value, color="red", arrow=False)
        print_arr("-" * 25, color="green")

    if print_output is False:
        ind = len(text)

    while True:
        try:
            user_choice = input("> ").lower()

            if (len(user_choice) > 3
                or int(user_choice) <= 0
                or int(user_choice) > ind):  raise ValueError

            else:
                return text[int(user_choice) - 1]

        except ValueError:
            print_arr(f"{user_choice} не существует!", color="red")


@KeyboardError()
def password_user(ssid: str) -> str:
    """ Функция для ввода пароля """

    print_arr(f"Введите пароль от {ssid}", color="green")

    while True:
        user_choice = input("> ")

        if len(user_choice) < 8 or len(user_choice) > 64:
            print_arr("Пароль должен состоять от 8 символов и до 64, ",
            "повторите попытку!", color="red")

        else:
            return user_choice


