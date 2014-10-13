from sys import stderr, exit
import shutil
import os
from resources import read_template, get_resource_root, get_kernel, get_kernel_inc
from project import Project

def execute(packages, site_only=False, init=False):
    project = Project()
    for package in packages:
        project.install(package, site_only, init=init)
