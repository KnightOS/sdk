import sys
import os
from knightos.workspace import Workspace

def execute(key):
    ws = Workspace()
    result = ws.config.get(key)
    if result == None:
        sys.exit(1)
    sys.stdout.write(result)
    sys.exit(0)
