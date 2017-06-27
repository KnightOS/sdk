import os
import sys
import json
from knightos.config import Config

def _find_root():
    path = os.getcwd()
    while True:
        if ".knightos" in os.listdir(path):
            if not os.path.isdir(os.path.join(path, ".knightos")):
                print(".knightos is present, but not a directory")
                sys.exit(1)
            return path
        _path = os.path.realpath(os.path.join(path, ".."))
        if _path == path:
            print("There doesn't seem to be a KnightOS project here. Did you run `knightos init`?")
            sys.exit(1)
        path = _path

def _collect_packages(ws):
    from knightos.package import Package
    _manifest = os.path.join(ws.kroot, "packages.manifest")
    if not os.path.exists(_manifest):
        manifest = list()
    else:
        with open(_manifest) as f:
            manifest = [Package(p) for p in json.loads(f.read())]
    packages = (ws.config.get("dependencies") or "").split(" ") + \
        (ws.config.get("-sdk-site-packages") or "").split(" ")
    ensure = list()
    for _p in packages:
        if ":" in _p:
            _ = p.split(":")
            p = Package.init_remote(_[0], _[1])
        else:
            p = Package.init_remote(_p)
        existing = next((package \
                for package in manifest \
                if package.name == p.name), None)
        manifest.append(existing or p)
        if not existing or existing.version != p.version:
            ensure.append(existing or p)
            if existing:
                existing.version = p.version
    os.makedirs(os.path.dirname(_manifest))
    with open(_manifest, "w") as f:
        f.write(json.dumps([p.to_dict() for p in manifest]))
    return ensure, manifest

class Workspace:
    def __init__(self, root=None):
        self.root = root
        if self.root == None:
            self.root = _find_root()
        self.kroot = os.path.join(self.root, ".knightos")
        self.config = Config(self)
        self._ensure, self.manifest = _collect_packages(self)

    @property
    def name(self):
        repo = self.config.get("repo")
        name = self.config.get("name")
        return "{}/{}".format(repo, name)
