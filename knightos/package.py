from enum import Enum
from knightos.workspace import Workspace

class PackageSource(Enum):
    local = "local"
    remote = "remote"

class WorkspacePackage:
    def __init__(self, name, version="latest"):
        _name = name.split("/")
        self.repo = _name[0]
        self.name = _name[1]
        self.source = None
        self.path = None
        self._version = None

    @property
    def version(self):
        if self._version:
            return self._version
        return self._ws.config.get("version")

    @property
    def full_name(self):
        return "{}/{}".format(self.repo, self.name)

    @staticmethod
    def init_remote(name, version="latest"):
        pkg = WorkspacePackage(name)
        pkg._version = version
        pkg.source = PackageSource.remote
        pkg.path = None
        return pkg

    @staticmethod
    def init_local(path):
        _ws = Workspace(path)
        pkg = WorkspacePackage(_ws.name)
        pkg._ws = _ws
        pkg._version = None
        pkg.source = PackageSource.local
        pkg.path = os.path.realpath(path)

    @staticmethod
    def from_dict(d):
        name = "{}/{}".format(d["repo"], d["name"])
        pkg = WorkspacePackage(name)
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
