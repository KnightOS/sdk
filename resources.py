import os

def get_resource_root():
    # Tries a few common install locations
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    if os.path.isdir(path) and os.path.isdir(os.path.join(path, "templates")):
        return path
    path = "/usr/share/knightos"
    if os.path.isdir(path):
        return path
    path = "/usr/local/share/knightos"
    if os.path.isdir(path):
        return path
    path = "C:\\KnightOS"
    if os.path.isdir(path):
        return path
    raise Exception("Unable to locate SDK resources")

def get_kernel():
    return os.path.join(get_resource_root(), "kernel", "kernel-ti84pSE.rom")
