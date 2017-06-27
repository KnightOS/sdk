import os

class Config:
    def __init__(self, workspace):
        self._config = dict()
        self._path = os.path.join(workspace.root, "package.config")
        lines = None
        with open(self._path) as f:
            lines = f.readlines()
        for line in lines:
            if not "=" in line:
                continue
            key = line.split("=")[0].strip()
            self._config[key] = line[line.index('=') + 1:].strip()

    def get(self, key):
        return self._config.get(key)

    def set(self, key, value):
        self._config[key] = value
        with open(self._path, "w") as f:
            for key in self._config:
                value = self._config[key]
                f.write("{}={}\n".format(key, value))
