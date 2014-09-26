from sys import stderr, exit
from os import getcwd, makedirs, listdir
from os.path import relpath, dirname, join
from project import Project
from util import resource

gitignore = """
product
build
.knightos
"""

sample = resource("sample.asm").read()

def execute(root=None):
    if root == None: root = getcwd()
    create_dir(root)
    proj = Project(root)
    proj.open(".gitignore", "w+").write(gitignore)
    proj.open("main.asm", "w+").write(sample)
    

def create_dir(root):
    makedirs(root, mode=0o755, exist_ok=True)
    if len(listdir(root)) > 0:
        stderr.write("{path} not empty. Aborting.\n".format(path=relpath(root)))
        exit(1)
