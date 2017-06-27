import os
import sys
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

class Workspace:
    def __init__(self, root=None):
        self.root = root
        if self.root == None:
            self.root = _find_root()
        self.config = Config(self)

    @property
    def name(self):
        repo = self.config.get("repo")
        name = self.config.get("name")
        return "{}/{}".format(repo, name)
