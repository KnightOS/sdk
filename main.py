#!/usr/bin/env python3
"""KnightOS SDK

Usage:
  knightos init [<projectroot>]
  knightos build
  knightos run
  knightos deploy
  knightos -h | --help
  knightos --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  

"""
from docopt import docopt
from init import execute as cmd_init
from build import execute as cmd_build
from run import execute as cmd_run
from deploy import execute as cmd_deploy

args = docopt(__doc__, version="0.0.1")

if args["init"]: cmd_init(root=args["<projectroot>"])
elif args["build"]: cmd_build()
elif args["run"]: cmd_run()
elif args["deploy"]: cmd_deploy()
