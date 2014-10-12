import os
import shutil

def resource(path, mode="r"):
    return open(os.path.join(os.path.dirname(__file__), path), mode=mode)

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

# Replacement for shutil.which, which wasn't introduced until python 3.3
def which(filename):
    locations = os.environ.get("PATH").split(os.pathsep)
    candidates = []
    for location in locations:
        candidate = os.path.join(location, filename)
        if os.path.isfile(candidate):
            candidates.append(candidate)
    return candidates
