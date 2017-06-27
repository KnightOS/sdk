from enum import Enum
from knightos.workspace import Workspace

class PackageSource(Enum):
    local = "local"
    remote = "remote"

class Package:
    def __init__(self, name, version="latest"):
        _name = name.split("/")
        self.repo = _name[0]
        self.name = _name[1]
        self.source = None
        self.path = None
        self._version = None

    @property
    def version(self):
        if pkg._version:
            return pkg._version
        return pkg._ws.config.get("version")

    @staticmethod
    def init_remote(name, version="latest"):
        pkg = Package(name)
        pkg._version = version
        pkg.source = PackageSource.remote
        pkg.path = None
        return pkg

    @staticmethod
    def init_local(path):
        _ws = Workspace(path)
        pkg = Package(_ws.name)
        pkg._ws = _ws
        pkg._version = None
        pkg.source = PackageSource.local
        pkg.path = os.path.realpath(path)

    @staticmethod
    def from_dict(d):
        name = "{}/{}".format(d["repo"], d["name"])
        pkg = Package(name)
        pkg._version = d["version"]
        pkg.source = PackageSource(d["source"])
        pkg.path = d["path"]
        if pkg.source == PackageSource.local:
            pkg._ws = Workspace(pkg.path)
        return pkg

    def to_dict(self):
        return {
            "repo": self.repo,
            "name": self.name,
            "version": self._version,
            "source": self.source.value,
            "path": self.path
        }
