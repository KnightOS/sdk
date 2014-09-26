import toml
from sys import exit, stderr
from os.path import join, realpath
from os import listdir, getcwd

class Project:
    def __init__(self, root=None):
        self.root = root
        if self.root == None: self.root = findroot()

    def __del__(self):
        pass
        # self.configfile.write(toml.dumps(self.config))

    def open(self, path, mode="r"):
        return open(join(self.root, path), mode=mode) # TODO: This leaks file descriptors

def findroot():
    path = getcwd()
    while path != "/": # TODO: Confirm this is cross platform
        if listdir(path).index("knightos.toml") >= 0:
            return path
        else:
            path = realpath(join(path, ".."))
    errmsg = "No `knightos.toml' found in any parent of {cwd}.\n"
    stderr.write(errmsg.format(cwd=getcwd()))
    exit(1)
