import os
import requests
from sys import stderr, exit
from resources import get_resource_root

def get_key(platform):
    if platform == "TI73": return 0x02
    if platform == "TI83p" or platform == "TI83pSE": return 0x04
    if platform == "TI84p" or platform == "TI84pSE": return 0x0A
    if platform == "TI84pCSE": return 0x0F

def get_upgrade_ext(platform):
    if platform == "TI73": return '73u'
    if platform == "TI84pCSE": return '8cu'
    return '8xu'

def get_privileged(platform):
    if platform == "TI73": return 0x1C
    if platform == "TI83p": return 0x1C
    if platform == "TI83pSE": return 0x7C
    if platform == "TI84p": return 0x3C
    if platform == "TI84pSE": return 0x7C
    if platform == "TI84pCSE": return 0xFC

def get_fat(platform):
    if platform == "TI73": return 0x17
    if platform == "TI83p": return 0x17
    if platform == "TI83pSE": return 0x77
    if platform == "TI84p": return 0x37
    if platform == "TI84pSE": return 0x77
    if platform == "TI84pCSE": return 0xF7
