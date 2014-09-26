import os
import requests
from sys import stderr, exit
from resources import get_resource_root

def prepare_environment():
    kernel = os.path.join(get_resource_root(), "kernel")
    os.makedirs(kernel, mode=0o755, exist_ok=True)
    kernels = [ "ti73", "ti83p", "ti83pSE", "ti84p", "ti84pSE", "ti84pCSE" ]
    update = False
    for k in kernels:
        path = os.path.join(kernel, "kernel-{0}.rom".format(k))
        if not os.path.isfile(path):
            update = True
            break
    if not os.path.isfile(os.path.join(kernel, "kernel.inc")):
        update = True
    if update:
        update_kernel()

def update_kernel():
    print("Grabbing latest KnightOS kernel from GitHub...")
    kernel_root = os.path.join(get_resource_root(), "kernel")
    release = get_latest_kernel()
    for asset in release['assets']:
        print("Downloading {0}...".format(asset['name']))
        r = requests.get(asset['browser_download_url'])
        with open(os.path.join(kernel_root, asset['name']), 'wb') as fd:
            for chunk in r.iter_content(1024):
                fd.write(chunk)
    with open(os.path.join(kernel_root, 'version'), 'w') as f:
        f.write(release['tag_name'])
    print("Updated to kernel {0}.".format(release['tag_name']))

def get_latest_kernel():
    releases = requests.get('https://api.github.com/repos/KnightOS/kernel/releases')
    return releases.json()[0]
