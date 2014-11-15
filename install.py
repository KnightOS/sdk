from sys import stderr, exit
import shutil
import os
from resources import read_template, get_resource_root, get_kernel
from project import Project

def execute(packages, site_only=False, init=False):
    project = Project()
    project.install(packages, site_only, init=init)
