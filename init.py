from sys import stderr, exit, stdout
import shutil
import subprocess
import os
import requests
import yaml
import pystache
from resources import get_resource_root, get_kernel
from project import Project
from knightos import get_key, get_upgrade_ext, get_fat, get_privileged
from util import copytree, which
from install import execute as cmd_install

def execute(project_name=None, emulator=None, debugger=None, assembler=None, platform=None, vcs=None, kernel_source=None, compiler=None, template=None):
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
        if proj.get_config("-sdk-template"):
            template=proj.get_config("-sdk-template").split(" ")
        if proj.get_config("-sdk-site-packages"):
            site_packages=proj.get_config("-sdk-site-packages").split(" ")
    template_yaml = yaml.load(open(os.path.join(get_resource_root(), "templates", template, template+".yaml"), 'r'))
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
        'kernel_path': kernel_source
    }
    init(proj, root, exists, site_packages, template_yaml, template_vars, vcs)

def init(proj, root, exists, site_packages, template, template_vars, vcs):
    print("Installing SDK...")
    if template_vars['kernel_path'] == None:
        install_kernel(os.path.join(root, ".knightos"), template_vars['platform'])
        shutil.move(os.path.join(root, ".knightos", "kernel-" + template_vars['platform'] + ".rom"), os.path.join(root, ".knightos", "kernel.rom"))

    print("Installing template...")
    for i in template["files"]:
        if not os.path.exists(os.path.join(root, i["path"])):
            ofile = open(os.path.join(get_resource_root(), "templates", template["name"], i["template"]), "r")
            if ofile == "sdk-custom-kernel.make" and template_vars['kernel_path'] == 'None': pass
            if ofile == "gitignore" and vcs != "git": pass
            file = open(os.path.join(root, i["path"]), "w")
            file.write(pystache.render(ofile.read(), template_vars))

    # TODO: Check for software listed in template['requries']

    print("Installing packages...")
    packages = proj.get_config("dependencies")
    if not packages:
        packages = list()
    else:
        packages = packages.split(' ')
    for i in template["install"]:
        if not i in packages:
            packages.append(i)
    cmd_install(packages, site_only=True, init=True)
    if len(site_packages) != 0:
        print("Installing site packages...")
        cmd_install(site_packages, site_only=True, init=True)
    if which('git') and vcs == "git":
        if not os.path.exists(os.path.join(root, ".git")):
            print("Initializing new git repository...")
            subprocess.call(["git", "init", root], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
    elif which('hg') and vcs == "hg":
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
    if exists and not os.path.exists(os.path.join(root, "package.config")):
        stderr.write("This directory is not empty and does not appear to have a KnightOS project, aborting!\n")
        exit(1)
    os.makedirs(os.path.join(root, ".knightos"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "include"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "packages"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "pkgroot"), mode=0o755)
    return exists

def install_kernel(root, platform):
    releases = requests.get('https://api.github.com/repos/KnightOS/kernel/releases')
    release = releases.json()[0]
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
