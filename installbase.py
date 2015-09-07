from sys import stderr, exit
import shutil
import os
from resources import get_resource_root, get_kernel
from project import Project

packages = ['core/castle', 'core/threadlist', 'extra/fileman', 'core/settings', 'core/configlib'];
def execute(site_only=True, init=True):
    project = Project()
    return project.install(packages, site_only, init=init)
