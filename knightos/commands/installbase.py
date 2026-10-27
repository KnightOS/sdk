import os
from knightos.workspace import Workspace

packages = [
    "core/castle",
    "core/threadlist",
    "extra/fileman",
    "core/settings",
    "core/configlib"
]

links = {
    "launcher": "/bin/castle",
    "switcher": "/bin/threadlist",
    "browser": "/bin/fileman",
}

def execute():
    ws = Workspace()
    for package in packages:
        ws.install_package(package)
	bin_dir = os.path.join(ws.kroot, "pkgroot", "bin")
    os.makedirs(bin_dir, exist_ok=True)
    for name, target in links.items():
        path = os.path.join(bin_dir, name)
        if os.path.lexists(path):
            os.remove(path)
        os.symlink(target, path)
