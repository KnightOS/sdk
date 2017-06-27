import os
import sys
import json
from knightos.util import http_get

# TODO: Non-XDG platforms (Windows, OSX)
_repo_path = os.environ.get("KNIGHTOS_CACHE") or os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(
            os.environ.get("HOME"), ".cache"), "knightos")
os.makedirs(_repo_path, exist_ok=True)

def _package_path(name, version=None):
    path = os.path.join(_repo_path,
            name,
            "latest" if version == None else "{}-{}.pkg".format(name, version))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.islink(path):
        path = os.path.join(_repo_path,
            name, os.readlink(path))
    return path

def get_manifest(name):
    path = _package_path(name)
    dirname = os.path.dirname(path)
    manifest_path = os.path.join(dirname, "manifest.json")
    if not os.path.exists(manifest_path):
        return None
    with open(manifest_path) as f:
        manifest = json.loads(f.read())
    return manifest

def _update_manifest(name):
    global _network
    path = _package_path(name)
    dirname = os.path.dirname(path)
    manifest_path = os.path.join(dirname, "manifest.json")
    r = http_get("https://packages.knightos.org/api/v1/" + name)
    if r:
        manifest = r.json()
        with open(manifest_path, "w") as f:
            f.write(json.dumps(manifest, indent=2))
    else:
        if not os.path.exists(manifest_path):
            print("Unable to download manifest for {}. Does it exist?".format(name))
            return None
        with open(manifest_path) as f:
            manifest = json.loads(f.read())
    version = manifest["version"]
    latest = os.path.join(os.path.dirname(path), "latest")
    if os.path.exists(latest):
        os.unlink(latest)
    os.symlink(
            "{}-{}.pkg".format(os.path.basename(name), version),
            latest)
    return manifest

def _download_package(name, version):
    manifest = _update_manifest(name)
    path = _package_path(name, version)
    if not manifest:
        return None
    sys.stdout.write("Downloading {}".format(os.path.basename(name)))
    with open(path, mode="wb") as f:
        _r = http_get(
            'https://packages.knightos.org/{}/download'.format(
                manifest['full_name']))
        total = int(_r.headers.get('content-length'))
        length = 0
        for chunk in _r.iter_content(1024):
            f.write(chunk)
            length += len(chunk)
            if sys.stdout.isatty():
                sys.stdout.write(
                        "\rDownloading {:<20} {:<20}".format(
                            name, str(int(length / total * 100)) + '%'))
    sys.stdout.write("\n")
    return path

def ensure_package(name, version=None):
    """
    Fetches a package if necessary and returns its path in the cache.
    """
    path = _package_path(name, version)
    if not os.path.exists(path):
        path = _download_package(name, version)
    manifest = _update_manifest(name) if path else None
    return path, manifest
