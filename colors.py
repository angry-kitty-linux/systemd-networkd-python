#!/usr/bin/python

from typing import Union

def print_arr(*text: Union[int, str, float], color:str, arrow = True) -> str:
    colors = {"red":"\033[31m", "blue":"\033[34m", "green":"\033[32m",
            "yellow":"\033[33m"}
    
    assert color in colors.keys()
    
    if arrow is True:
        print (f"{colors[color]}==> ", end = "")

    if arrow is False:
        print (f"{colors[color]}", end = "")

    print (*text, sep = "")
    print ("\033[0m", end = "")
