from sys import stderr, exit
import shutil
import os
from knightos.workspace import Workspace

def execute(packages, site_only=False, init=False, local_path=None):
    ws = Workspace()
    for package in packages:
        if site_only:
            ws.install_package(package, local_path=local_path)
        else:
            ws.require_package(package, local_path=local_path)
