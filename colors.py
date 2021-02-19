#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Union

<<<<<<< HEAD
def print_arr(*text: Union[int, str, float], color:str, arrow:bool = True, return_color:bool = False) -> str:
    colors = {"red":"\033[31m", "blue":"\033[34m", "green":"\033[32m",
            "yellow":"\033[33m", "white":"\033[39m", "pink":"\033[95m"}
    
    assert color in colors.keys()
    
    if arrow is True and return_color is False:
        print (f"{colors[color]}==> ", end = "")

    else:
        print (f"{colors[color]}", end = "")

    if return_color is False:
        print (*text, sep = "")
        print ("\033[0m", end = "")

    if return_color is True:
        return "{0}{1}\033[0m".format(colors[color], *text)

=======
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
>>>>>>> e77968b333a911e7786499eb7dc6a9e6620b3747
