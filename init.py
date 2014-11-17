from sys import stderr, exit, stdout
import shutil
import subprocess
import os
import requests
from resources import read_template, get_resource_root, get_kernel
from project import Project
from knightos import get_key, get_upgrade_ext, get_fat, get_privileged
from util import copytree, which
from install import execute as cmd_install

def execute(project_name=None, emulator=None, debugger=None, assembler=None, platform=None, vcs=None, kernel_source=None, compiler=None, language=None):
    root = os.getcwd()
    exists = setup_root(root, project_name)
    proj = Project(root)
    site_packages = []
    if exists and not project_name:
        project_name = proj.get_config("name")
        print("Found existing project: " + project_name)
        # Grab project-specific options
        if proj.get_config("-sdk-emulator"):
            emulator=proj.get_config("-sdk-emulator")
        if proj.get_config("-sdk-debugger"):
            emulator=proj.get_config("-sdk-debugger")
        if proj.get_config("-sdk-assembler"):
            emulator=proj.get_config("-sdk-assembler")
        if proj.get_config("-sdk-compiler"):
            compiler=proj.get_config("-sdk-compiler")
        if proj.get_config("-sdk-language"):
            language=proj.get_config("-sdk-language")
        if proj.get_config("-sdk-site-packages"):
            site_packages=proj.get_config("-sdk-site-packages").split(" ")
    template_vars = {
        'project_name': project_name,
        'assembler': assembler,
        'compiler': compiler,
        'emulator': emulator,
        'debugger': debugger,
        'platform': platform,
        'key': '{:02X}'.format(get_key(platform)),
        'upgrade_ext': get_upgrade_ext(platform),
        'fat': '{:02X}'.format(get_fat(platform)),
        'privileged': '{:02X}'.format(get_privileged(platform)),
        'kernel_path': str(kernel_source)
    }
    if language == 'assembly':
        init_assembly(proj, root, exists, site_packages, template_vars, vcs)
    else:
        init_c(proj, root, exists, site_packages, template_vars, vcs)

def init_assembly(proj, root, exists, site_packages, template_vars, vcs):
    print("Installing SDK...")
    if template_vars['kernel_path'] == 'None':
        proj.open(os.path.join(root, ".knightos", "sdk.make"), "w+").write(read_template("assembly/sdk.make", template_vars))
    else:
        proj.open(os.path.join(root, ".knightos", "sdk.make"), "w+").write(read_template("assembly/sdk-custom-kernel.make", template_vars))
    proj.open(os.path.join(root, ".knightos", "variables.make"), "w+").write(read_template("assembly/variables.make", template_vars))
    if template_vars['kernel_path'] == 'None':
        install_kernel(os.path.join(root, ".knightos"), template_vars['platform'])
        shutil.move(os.path.join(root, ".knightos", "kernel-" + template_vars['platform'] + ".rom"), os.path.join(root, ".knightos", "kernel.rom"))

    print("Installing templates...")
    if not os.path.exists(os.path.join(root, ".gitignore")):
        proj.open(os.path.join(root, ".gitignore"), "w+").write(read_template("assembly/gitignore", template_vars))
    if not exists:
        proj.open(os.path.join(root, "main.asm"), "w+").write(read_template("assembly/main.asm", template_vars))
    if not os.path.exists(os.path.join(root, "Makefile")):
        proj.open(os.path.join(root, "Makefile"), "w+").write(read_template("assembly/Makefile", template_vars))
    if not os.path.exists(os.path.join(root, "package.config")):
        proj.open(os.path.join(root, "package.config"), "w+").write(read_template("assembly/package.config", template_vars))

    print("Installing packages...")
    packages = proj.get_config("dependencies")
    if packages == None:
        packages = ["core/kernel-headers", "core/init"]
    else:
        packages = packages.split(" ")
        # Required packages
        if not "core/kernel-headers" in packages:
            packages.append("core/kernel-headers")
        if not "core/init" in packages:
            packages.append("core/init")
    cmd_install(packages, site_only=True, init=True)
    if len(site_packages) != 0:
        print("Installing site packages...")
        cmd_install(site_packages, site_only=True, init=True)
    if which('git') != None and vcs == "git":
        if not os.path.exists(os.path.join(root, ".git")):
            print("Initializing new git repository...")
            subprocess.call(["git", "init", root], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
    elif which('hg') != None and vcs == "hg":
        if not os.path.exists(os.path.join(root, ".hg")):
            print("Initializing new hg repository...")
            subprocess.call(["hg", "init", root], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
    print("All done! You can use `make help` to find out what to do next.")

def init_c(proj, root, exists, site_packages, template_vars, vcs):
    template_vars['assembler'] = 'scas' # Temporary
    print("Installing SDK...")
    proj.open(os.path.join(root, ".knightos", "sdk.make"), "w+").write(read_template("c/sdk.make", template_vars))
    proj.open(os.path.join(root, ".knightos", "variables.make"), "w+").write(read_template("c/variables.make", template_vars))
    install_kernel(os.path.join(root, ".knightos"), template_vars['platform'])
    shutil.move(os.path.join(root, ".knightos", "kernel-" + template_vars['platform'] + ".rom"), os.path.join(root, ".knightos", "kernel.rom"))

    print("Installing templates...")
    if not os.path.exists(os.path.join(root, ".gitignore")):
        proj.open(os.path.join(root, ".gitignore"), "w+").write(read_template("c/gitignore", template_vars))
    if not exists:
        proj.open(os.path.join(root, "main.c"), "w+").write(read_template("c/main.c", template_vars))
    if not exists:
        proj.open(os.path.join(root, "crt0.asm"), "w+").write(read_template("c/crt0.asm", template_vars))
    if not os.path.exists(os.path.join(root, "Makefile")):
        proj.open(os.path.join(root, "Makefile"), "w+").write(read_template("c/Makefile", template_vars))
    if not os.path.exists(os.path.join(root, "package.config")):
        proj.open(os.path.join(root, "package.config"), "w+").write(read_template("c/package.config", template_vars))

    print("Installing packages...")
    packages = proj.get_config("dependencies")
    if packages == None:
        packages = ["core/kernel-headers", "core/init"]
    else:
        packages = packages.split(" ")
        # Required packages
        if not "core/kernel-headers" in packages:
            packages.append("core/kernel-headers")
        if not "core/init" in packages:
            packages.append("core/init")
    cmd_install(packages, site_only=True, init=True)
    if len(site_packages) != 0:
        print("Installing site packages...")
        cmd_install(site_packages, site_only=True, init=True)
    if which('git') != None and vcs == "git":
        if not os.path.exists(os.path.join(root, ".git")):
            print("Initializing new git repository...")
            subprocess.call(["git", "init", root], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
    elif which('hg') != None and vcs == "hg":
        if not os.path.exists(os.path.join(root, ".hg")):
            print("Initializing new hg repository...")
            subprocess.call(["hg", "init", root], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
    print("All done! You can use `make help` to find out what to do next.")

def setup_root(root, project_name):
    if os.path.exists(os.path.join(root, ".knightos")):
        shutil.rmtree(os.path.join(root, ".knightos"))
        print("Notice: Rebuilding existing environment")
    os.makedirs(root, mode=0o755, exist_ok=True)
    exists = False
    if len(os.listdir(root)) > 0:
        exists = True
    if not exists and not project_name:
        stderr.write("You must specify a project name for new projects.\n")
        exit(1)
    os.makedirs(os.path.join(root, ".knightos"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "include"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "packages"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "pkgroot"), mode=0o755)
    return exists

def install_kernel(root, platform):
    release = get_latest_kernel()
    print("Installing kernel " + release['tag_name'])
    assets = list()
    assets.append([r for r in release['assets'] if r['name'] == 'kernel-' + platform + '.rom'][0])
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
