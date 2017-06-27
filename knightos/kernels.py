import os
import sys
import json
from knightos.util import http_get

_kernel_path = os.environ.get("KNIGHTOS_CACHE") or os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(
            os.environ.get("HOME"), ".cache"), "knightos", "kernels")
os.makedirs(_kernel_path, exist_ok=True)

def _update_manifest():
    releases = http_get("https://api.github.com/repos/KnightOS/kernel/releases")
    _manifest_path = os.path.join(_kernel_path, "manifest.json")
    if not releases:
        if not os.path.exists(_manifest_path):
            return None
        with open(_manifest_path) as f:
            releases = json.loads(f.read())
    else:
        releases = releases.json()
        with open(_manifest_path, "w") as f:
            f.write(json.dumps(releases))
    return releases

def ensure_kernel(platform, version="latest"):
    manifest = _update_manifest()
    if version == "latest":
        release = manifest[0]
    else:
        release = next(
                (r for r in manifest if r["tag_name"] == version), None)
        if not release:
            print("Unable to obtain kernel version " + version)
            return None
    version = release["tag_name"]
    kernel_name = "knightos-{}-{}.rom".format(platform, version)
    asset = next((r for r in release["assets"] \
                if r["name"] == "kernel-" + platform + ".rom"), None)
    if not asset:
        print("Platform {} is not available for kernel {}".format(
            platform, version))
        return None
    path = os.path.join(_kernel_path, asset["name"])
    if os.path.exists(path):
        return path, version
    sys.stdout.write("Downloading {0}...".format(asset["name"]))
    r = http_get(asset["browser_download_url"])
    total = int(r.headers.get("content-length"))
    length = 0
    with open(path, "wb") as fd:
        for chunk in r.iter_content(1024):
            fd.write(chunk)
            length += len(chunk)
            if sys.stdout.isatty():
                sys.stdout.write("\rDownloading {:<20} {:<20}".format(asset['name'], str(int(length / total * 100)) + '%'))
    sys.stdout.write("\n")
    return path, version
