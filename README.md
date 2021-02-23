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

Если вы используете `Ubuntu`-подобные системы, могут возникнуть проблемы при установке pip.
Что-то типо этого:
`ModuleNotFoundError: No module named 'distutils.util'`

Чтобы это исправить вам нужно прописать следующую команду:
`$ sudo apt install python3-distutils`
