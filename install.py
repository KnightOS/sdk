from sys import stderr, exit
import shutil
import os
from resources import get_resource_root, get_kernel
from project import Project

def execute(packages, site_only=False, init=False):
    project = Project()
    return project.install(packages, site_only, init=init)
