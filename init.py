from sys import stderr, exit
import shutil
import os
from resources import read_template, get_resource_root, get_kernel, get_kernel_inc
from project import Project
from knightos import prepare_enviornment

def copytree(src, dst, symlinks=False, ignore=None): # shutil.copytree doesn't let you merge dirs
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
                shutil.copy2(s, d)

def execute(project_name, root=None):
    if root == None: root = os.getcwd()
    prepare_enviornment()
    setup_root(root)
    proj = Project(root)
    proj.open(os.path.join(root, ".gitignore"), "w+").write(read_template("gitignore", project_name))
    proj.open(os.path.join(root, "main.asm"), "w+").write(read_template("main.asm", project_name))
    proj.open(os.path.join(root, "Makefile"), "w+").write(read_template("Makefile", project_name))
    proj.open(os.path.join(root, ".knightos", "sdk.make"), "w+").write(read_template("sdk.make", project_name))
    proj.open(os.path.join(root, ".knightos", "variables.make"), "w+").write(read_template("variables.make", project_name))
    shutil.copyfile(get_kernel(), os.path.join(root, ".knightos", "kernel.rom"))
    shutil.copyfile(get_kernel_inc(), os.path.join(root, ".knightos", "include", "kernel.inc"))
    # Temporary - install a couple of required packages
    copytree(os.path.join(get_resource_root(), "templates", "temp", "base"), os.path.join(root, ".knightos", "pkgroot"))
    copytree(os.path.join(get_resource_root(), "templates", "temp", "corelib"), os.path.join(root, ".knightos", "pkgroot"))

def setup_root(root):
    os.makedirs(root, mode=0o755, exist_ok=True)
    if len(os.listdir(root)) > 0:
        stderr.write("{path} not empty. Aborting.\n".format(path=os.path.relpath(root)))
        exit(1)
    os.makedirs(os.path.join(root, ".knightos"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "include"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "pkgroot"), mode=0o755)
