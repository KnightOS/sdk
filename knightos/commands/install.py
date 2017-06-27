from sys import stderr, exit
import shutil
import os
from knightos.workspace import Workspace

def execute(packages, site_only=False, init=False):
    ws = Workspace()
    if site_only:
        [ws.install_package(package) for package in packages]
    else:
        [ws.require_package(package) for package in packages]
