from os.path import dirname, join
def resource(path, mode="r"):
    return open(join(dirname(__file__), path), mode=mode)
