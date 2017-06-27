from knightos.workspace import Workspace

packages = [
    "core/castle",
    "core/threadlist",
    "extra/fileman",
    "core/settings",
    "core/configlib"
]

def execute():
    ws = Workspace()
    for package in packages:
        ws.install_package(package)
