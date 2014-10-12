#!/usr/bin/env python3
"""KnightOS SDK

Usage:
  knightos init [<name>] [<root>]
  knightos install [--site-only] <packages>...
  knightos -h | --help
  knightos --version

Options:
  init          Initializes a new KnightOS project here or sets up an existing one
  install       Installs the specified packages
  --site-only   Installs the package but does not add it to package.config
  -h --help     Show this screen.
  --version     Show version.
  

"""
from docopt import docopt
from init import execute as cmd_init
from install import execute as cmd_install

args = docopt(__doc__, version="0.0.1")

if args["init"]: cmd_init(project_name=args["<name>"], root=args["<root>"])
if args["install"]: cmd_install(args["<packages>"], site_only=args["--site-only"])
