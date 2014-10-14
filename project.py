from sys import exit, stderr, stdout
from util import copytree

import os
import requests
import subprocess

class Project:
    def __init__(self, root=None):
        self.root = root
        if self.root == None: self.root = findroot()

    def __del__(self):
        pass

    def open(self, path, mode="r"):
        return open(os.path.join(self.root, path), mode=mode) # TODO: This leaks file descriptors

    def get_config(self, key):
        lines = None
        with self.open("package.config") as c:
            lines = c.readlines()
        for line in lines:
            if line.startswith(key):
                try:
                    return line[line.index('=') + 1:].strip()
                except:
                    pass
        return None

    def set_config(self, key, value):
        lines = None
        with self.open("package.config") as c:
            lines = c.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.startswith(key):
                lines[i] = key + '=' + value
                found = True
        if not found:
            lines.append("{0}={1}".format(key, value))
        if value == '':
            lines = [l for l in lines if not l.startswith(key)]
        with self.open("package.config", mode="w") as c:
            c.write(''.join(lines))

    def install(self, packages, site_only, init=False):
        deps = self.get_config("dependencies")
        if deps == None:
            deps = list()
        else:
            deps = deps.split(' ')
        for i, dep in enumerate(deps):
            if ':' in dep:
                deps[i] = dep.split(':')[0]
        for package in packages:
            info = requests.get('https://packages.knightos.org/api/v1/' + package)
            if info.status_code == 404:
                stderr.write("Cannot find '{0}' on packages.knightos.org.\n".format(package))
                exit(1)
            elif info.status_code != 200:
                stderr.write("An error occured while contacting packages.knightos.org for information.\n")
                exit(1)
            extra = list()
            for dep in info.json()['dependencies']:
                if not dep in deps:
                    print("Adding dependency: " + dep)
                    extra.append(dep)
        files = []
        all_packages = extra + packages
        # Download packages
        for p in all_packages:
            stdout.write("\rDownloading {0}".format(p))
            r = requests.get('https://packages.knightos.org/api/v1/' + p)
            path = os.path.join(self.root, ".knightos", "packages", "{0}-{1}.pkg".format(r.json()['name'], r.json()['version']))
            files.append(path)
            with self.open(path, mode="wb") as fd:
                _r = requests.get('https://packages.knightos.org/{0}/download'.format(r.json()['full_name']))
                total = int(_r.headers.get('content-length'))
                length = 0
                for chunk in _r.iter_content(1024):
                    fd.write(chunk)
                    length += len(chunk)
                    stdout.write("\rDownloading {:<20} {:<20}".format(p, str(int(length / total * 100)) + '%'))
            stdout.write("\n")
        if not site_only:
            for package in packages:
                deps.append(package)
        self.set_config("dependencies", " ".join(deps))
        # Install packages
        pkgroot = os.path.join(self.root, ".knightos", "pkgroot")
        for i, f in enumerate(files):
            print("Installing {0}...".format(all_packages[i]))
            FNULL = open(os.devnull, 'w')
            ret = subprocess.call(['kpack', '-e', f, pkgroot], stdout=FNULL, stderr=subprocess.STDOUT)
            ret = subprocess.call(['kpack', '-e', '-s', f, pkgroot], stdout=FNULL, stderr=subprocess.STDOUT)
            if ret != 0:
                stderr.write("kpack returned status code {0}, aborting\n".format(ret))
                exit(ret)
            # Copy include files, if they exist
            if os.path.exists(os.path.join(self.root, ".knightos", "pkgroot", "include")):
                copytree(os.path.join(self.root, ".knightos", "pkgroot", "include"), os.path.join(self.root, ".knightos", "include"))

def findroot():
    path = os.getcwd()
    while path != "/": # TODO: Confirm this is cross platform
        if ".knightos" in os.listdir(path):
            return path
        else:
            path = os.path.realpath(os.path.join(path, ".."))
    stderr.write("There doesn't seem to be a KnightOS project here. Did you run `knightos init`?\n")
    exit(1)
