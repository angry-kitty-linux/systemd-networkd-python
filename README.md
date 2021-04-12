Systemd-networkd-python
=======================

# Что это такое?

*Systemd-network-python* - это обвертка, которая должна вам помочь при конфигурации wpa_supplicant, с использованием systemd-networkd.

 БЫСТРЫЙ СТАРТ
 ------------------

`$ cd`

`$ git clone https://github.com/angry-kitty-linux/systemd-networkd-python`

`$ cd systemd-networkd-python`

`$ sudo python3 systemd-networkd-python`


Возможные проблемы
---------------------

Если вы столкнулись с какой-либо ошибкой, то попробуйте перезаписать профили.
Это вероятнее всего исправит вашу проблему.


Зависимости
---------------------
Программа предполагает что у вас установлен модуль `psutil`. Вы его можете установить
с помощью pip командой:

`$ sudo pip3 install psutil`

Или же через пакетный менеджер вашего дистрибутива

*Arch Linux*:
---
`$ yay -S python-psutil`

*Debian | Ubuntu | Linux Mint*:
---
`$ sudo apt install python-psutil`




Тестирование на других дистрибутивах
--------------------

|                            | Поддерживается |
|----------------------------|----------------|
| Arch Linux                 |       ✅       |
| Ubuntu                     |       ✅       |
| Linux Mint                 |       ✅       |
| Debian                     |       ✅       |
| Gentoo                     |       ❌       |
