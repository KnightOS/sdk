import os
import sys
import json
import shutil
import subprocess
import pystache
from knightos.config import Config
from knightos.repository import ensure_package

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
    from knightos.package import WorkspacePackage
    package_list = os.path.join(ws.kroot, "packages.list")
    if not os.path.exists(package_list):
        packages = list()
    else:
        with open(package_list) as f:
            packages = [WorkspacePackage.from_dict(p) for p in json.loads(f.read())]
    desired_packages = list()
    _deps = ws.config.get("dependencies")
    if _deps:
        desired_packages += _deps.split(" ")
    _deps = ws.config.get("-sdk-site-packages")
    if _deps:
        desired_packages += _deps.split(" ")
    desired_packages.append("core/kernel-headers")
    desired_packages.append("core/init")
    ensure = list()
    for package_name in desired_packages:
        if ":" in package_name:
            _ = package_name.split(":")
            new_package = WorkspacePackage.init_remote(_[0], _[1])
        else:
            new_package = WorkspacePackage.init_remote(package_name)
        existing_package = next((package \
            for package in packages \
            if package.name == new_package.name), None)
        package = existing_package or new_package
        if not existing_package:
            packages.append(package)
        if not existing_package or package.version != existing_package.version:
            ensure.append(package)
            if existing_package:
                package.version = new_package.version
    return ensure, packages

def _write_packages(ws):
    package_list = os.path.join(ws.kroot, "packages.list")
    os.makedirs(os.path.dirname(package_list), exist_ok=True)
    with open(package_list, "w") as f:
        f.write(json.dumps([p.to_dict() for p in ws.packages]))

def _gen_packages_make(ws):
    from knightos.package import PackageSource
    kwargs = {
        "remote_packages": [
            p for p in ws.packages if p.source == PackageSource.remote
        ] or None,
        "local_packages": [
            p for p in ws.packages if p.source == PackageSource.local
        ] or None,
    }
    slib = os.path.join(ws.kroot, "pkgroot", "slib")
    if os.path.exists(slib):
        kwargs["static_libs"] = []
        for root, dirs, files in os.walk(slib):
            for library in files:
                kwargs["static_libs"].append({
                    "path": os.path.join(slib, library)
                })
    template_src = os.path.join(os.path.dirname(__file__), "templates", "packages.make")
    with open(template_src) as template:
        path = os.path.join(ws.kroot, "packages.make")
        with open(os.path.join(path), "w") as f:
            f.write(pystache.render(template.read(), kwargs))

class Workspace:
    def __init__(self, root=None):
        self.root = root
        if self.root == None:
            self.root = _find_root()
        self.kroot = os.path.join(self.root, ".knightos")
        self.config = Config(self)
        self._ensure, self.packages = _collect_packages(self)

    @property
    def name(self):
        repo = self.config.get("repo")
        name = self.config.get("name")
        return "{}/{}".format(repo, name)

    def require_package(self, package):
        self.install_package(package)
        deps = self.config.get("dependencies")
        if not deps:
            deps = list()
            normalized_deps = list()
        else:
            deps = deps.split(" ")
            normalized_deps = [
                d.split(":")[0] if ":" in d else d \
                for d in deps
            ]
        if not any([d for d in normalized_deps if d == package]):
            deps.append(package)
            self.config.set("dependencies",
                    " ".join(deps))

    def install_package(self, package, gen_packages_make=True):
        from knightos.package import WorkspacePackage
        packages = os.path.join(self.kroot, "packages")
        pkgroot = os.path.join(self.kroot, "pkgroot")
        os.makedirs(packages, exist_ok=True)
        os.makedirs(pkgroot, exist_ok=True)
        _package = next((p for p in self.packages if p.full_name == package), None)
        if not _package:
            package = WorkspacePackage.init_remote(package)
            self.packages.append(package)
        else:
            package = _package
        source, manifest = ensure_package(package.full_name)
        if not source or not manifest:
            sys.exit(1)
        if not _package:
            _write_packages(self)
        package._version = manifest["version"]
        print("Installing {}...".format(package.full_name))
        dest = os.path.join(packages, os.path.basename(source))
        if os.path.exists(dest):
            os.remove(dest)
        os.symlink(source, dest)
        FNULL = open(os.devnull, 'w')
        subprocess.call(["kpack", "-e",
            dest, pkgroot], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(["kpack", "-e", "-s",
            dest, pkgroot], stdout=FNULL, stderr=subprocess.STDOUT)
        if gen_packages_make:
            _gen_packages_make(self)

    def ensure_packages(self):
        packages = os.path.join(self.kroot, "packages")
        os.makedirs(packages, exist_ok=True)
        for package in self._ensure:
            self.install_package(package.full_name, gen_packages_make=False)
        _write_packages(self)
        _gen_packages_make(self)
