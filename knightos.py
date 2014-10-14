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
