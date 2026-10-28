from sys import stderr, exit
from knightos.workspace import Workspace

def execute(packages, keep_installed=False):
    ws = Workspace()
    success = True
    for package in packages:
        if len(package.split("/")) != 2:
            print("Invalid package name {0}. Format should be `repository/package`.".format(package))
            success = False
            continue
        if not ws.uninstall_package(package, keep_installed=keep_installed):
            success = False
    if not success:
        sys.exit(1)
