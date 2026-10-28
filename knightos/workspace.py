import os
import re
import sys
import glob
import json
import shutil
import tempfile
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
    if os.path.exists(os.path.join(ws.kroot, "kernel-version")):
        _packages = ws.packages
    else:
        # Omit kernel-headers when using a custom kernel
        _packages = [p for p in ws.packages if p.full_name != "core/kernel-headers"]
    kwargs = {
        "remote_packages": [
            p for p in _packages if p.source == PackageSource.remote
        ] or None,
        "local_packages": [
            p for p in _packages if p.source == PackageSource.local
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

# Always installed by the SDK (see _collect_packages): uninstalling them is pointless.
_required_packages = ["core/kernel-headers", "core/init"]

def _remove_from_config_list(ws, key, package):
    """Removes `package` (with or without `:version`) from a space-separated
    list in package.config. Returns True if it was present."""
    value = ws.config.get(key)
    if not value:
        return False
    items = value.split(" ")
    kept = [i for i in items if i.split(":")[0] != package]
    if len(kept) == len(items):
        return False
    if kept:
        ws.config.set(key, " ".join(kept))
    else:
        ws.config.remove(key)
    return True

def _package_links(ws, package):
    """Links to the installed .pkg file in .knightos/packages/"""
    packages = os.path.join(ws.kroot, "packages")
    if not os.path.isdir(packages):
        return []
    pattern = re.compile(r"^{}-\d.*\.pkg$".format(re.escape(package.name)))
    return [os.path.join(packages, f) for f in os.listdir(packages) if pattern.match(f)]

def _package_file(ws, package):
    from knightos.package import PackageSource
    files = [l for l in _package_links(ws, package) if os.path.exists(l)]
    if not files and package.source == PackageSource.local:
        files = glob.glob(os.path.join(package.path, "{}-*.pkg".format(package.name)))
    return files[0] if files else None

def _package_dependencies(pkg_file):
    try:
        info = subprocess.run(["kpack", "-i", pkg_file],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    except (OSError, subprocess.CalledProcessError):
        return []
    for line in info.stdout.decode().splitlines():
        if line.startswith("dependencies="):
            return [d.split(":")[0] for d in line[len("dependencies="):].split()]
    return []

def _remove_file(base, rel):
    path = os.path.join(base, rel)
    if not os.path.lexists(path) or os.path.isdir(path):
        return
    os.remove(path)
    # Also remove the directories that are left empty
    parent = os.path.dirname(path)
    while parent != base and not os.listdir(parent):
        os.rmdir(parent)
        parent = os.path.dirname(parent)

def _remove_extracted_files(ws, pkg_file):
    """Removes from pkgroot/ (and include/) the files extracted from pkg_file
    by packages.make (kpack -e and kpack -e -s)."""
    pkgroot = os.path.join(ws.kroot, "pkgroot")
    include = os.path.join(ws.kroot, "include")
    with tempfile.TemporaryDirectory() as tmp:
        for flags in (["-e"], ["-e", "-s"]):
            subprocess.run(["kpack"] + flags + [pkg_file, tmp],
                    stdout=subprocess.DEVNULL, check=True)
        for dirpath, _, filenames in os.walk(tmp):
            for filename in filenames:
                rel = os.path.relpath(os.path.join(dirpath, filename), tmp)
                _remove_file(pkgroot, rel)
                if rel.startswith("include" + os.sep):
                    _remove_file(include, os.path.relpath(rel, "include"))


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

    def require_package(self, package, local_path=None):
        self.install_package(package, local_path = local_path)
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

    def install_package(self, package, gen_packages_make=True, local_path=None):
        from knightos.package import WorkspacePackage
        from knightos.package import PackageSource
        packages = os.path.join(self.kroot, "packages")
        pkgroot = os.path.join(self.kroot, "pkgroot")
        os.makedirs(packages, exist_ok=True)
        os.makedirs(pkgroot, exist_ok=True)
        _package = next((p for p in self.packages if p.full_name == package), None)
        if not _package:
            if local_path:
                package = WorkspacePackage.init_local(local_path)
            else:
                package = WorkspacePackage.init_remote(package)
            self.packages.append(package)
        else:
            package = _package
        if local_path:
            if package.source == PackageSource.remote:
                print("Overriding remote package...")
                self.packages.remove(package)
                package = WorkspacePackage.init_local(local_path)
                self.packages.append(package)
                _package = None
            source = os.path.join(package.path, "{}-{}.pkg".format(
                package.name, package.version))
        else:
            source, manifest = ensure_package(package.full_name)
            if not source or not manifest:
                sys.exit(1)
            package._version = manifest["version"]
        if not _package:
            _write_packages(self)
        print("Installing {}...".format(package.full_name))
        dest = os.path.join(packages, os.path.basename(source))
        if os.path.exists(dest):
            os.remove(dest)
        os.symlink(source, dest)
        if gen_packages_make:
            _gen_packages_make(self)

    def uninstall_package(self, package, keep_installed=False):
        if package in _required_packages:
            print("{} is required by the SDK and cannot be uninstalled.".format(package))
            return False
        was_dependency = _remove_from_config_list(self, "dependencies", package)
        if keep_installed:
            if was_dependency:
                print("Removed {} from package.config.".format(package))
            else:
                print("{} is not a dependency of this project.".format(package))
            return was_dependency
        _remove_from_config_list(self, "-sdk-site-packages", package)
        _package = next((p for p in self.packages if p.full_name == package), None)
        if not _package:
            if was_dependency:
                print("Removed {} from package.config.".format(package))
                return True
            print("{} is not installed.".format(package))
            return False
        for other in self.packages:
            if other is _package:
                continue
            pkg_file = _package_file(self, other)
            if pkg_file and package in _package_dependencies(pkg_file):
                print("Warning: {} depends on {}.".format(other.full_name, package))
        print("Uninstalling {}...".format(package))
        pkg_file = _package_file(self, _package)
        removed_files = False
        if pkg_file:
            try:
                _remove_extracted_files(self, pkg_file)
                removed_files = True
            except (OSError, subprocess.CalledProcessError):
                pass
        if not removed_files:
            print("Warning: unable to read the package file, its files were left in .knightos/pkgroot/")
        for link in _package_links(self, _package):
            os.remove(link)
        self.packages.remove(_package)
        _write_packages(self)
        _gen_packages_make(self)
        return True

    def ensure_packages(self):
        packages = os.path.join(self.kroot, "packages")
        os.makedirs(packages, exist_ok=True)
        for package in self._ensure:
            self.install_package(package.full_name, gen_packages_make=False)
        _write_packages(self)
        _gen_packages_make(self)
