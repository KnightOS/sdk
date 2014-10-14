from sys import stderr, exit, stdout
from project import Project
import os

def execute(key, root=None):
    if root == None: root = os.getcwd()
    proj = Project(root)
    result = proj.get_config(key)
    if result == None:
        exit(1)
    stdout.write(result)
    exit(0)
