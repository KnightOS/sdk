from sys import stderr, exit, stdout
import shutil
import os
import requests
from resources import read_template, get_resource_root, get_kernel, get_kernel_inc
from project import Project
from knightos import prepare_environment
from util import copytree
from install import execute as cmd_install

def execute(project_name, root=None):
    if root == None: root = os.getcwd()
    print("Installing templates...")
    setup_root(root)
    proj = Project(root)
    proj.open(os.path.join(root, ".gitignore"), "w+").write(read_template("gitignore", project_name))
    proj.open(os.path.join(root, "main.asm"), "w+").write(read_template("main.asm", project_name))
    proj.open(os.path.join(root, "Makefile"), "w+").write(read_template("Makefile", project_name))
    proj.open(os.path.join(root, "package.config"), "w+").write(read_template("package.config", project_name))
    proj.open(os.path.join(root, ".knightos", "sdk.make"), "w+").write(read_template("sdk.make", project_name))
    proj.open(os.path.join(root, ".knightos", "variables.make"), "w+").write(read_template("variables.make", project_name))
    install_kernel(os.path.join(root, ".knightos"))
    shutil.move(os.path.join(root, ".knightos", "kernel.inc"), os.path.join(root, ".knightos", "include", "kernel.inc"))
    shutil.move(os.path.join(root, ".knightos", "kernel-TI84pSE.rom"), os.path.join(root, ".knightos", "kernel.rom"))
    default_packages = ["core/init"]
    print("Installing default packages...")
    for package in default_packages:
        cmd_install(package, site_only=True)

def setup_root(root):
    os.makedirs(root, mode=0o755, exist_ok=True)
    if len(os.listdir(root)) > 0:
        stderr.write("{path} not empty. Aborting.\n".format(path=os.path.relpath(root)))
        exit(1)
    os.makedirs(os.path.join(root, ".knightos"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "include"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "packages"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "pkgroot"), mode=0o755)

def install_kernel(root):
    release = get_latest_kernel()
    print("Installing kernel " + release['tag_name'])
    assets = list()
    assets.append([r for r in release['assets'] if r['name'] == 'kernel.inc'][0])
    assets.append([r for r in release['assets'] if r['name'] == 'kernel-TI84pSE.rom'][0])
    for asset in assets:
        stdout.write("\rDownloading {0}...".format(asset['name']))
        r = requests.get(asset['browser_download_url'])
        total = int(r.headers.get('content-length'))
        length = 0
        with open(os.path.join(root, asset['name']), 'wb') as fd:
            for chunk in r.iter_content(1024):
                fd.write(chunk)
                length += len(chunk)
                stdout.write("\rDownloading {:<20} {:<20}".format(asset['name'], str(int(length / total * 100)) + '%'))
        stdout.write("\n")
    with open(os.path.join(root, 'kernel-version'), 'w') as f:
        f.write(release['tag_name'])

def get_latest_kernel():
    releases = requests.get('https://api.github.com/repos/KnightOS/kernel/releases')
    return releases.json()[0]
