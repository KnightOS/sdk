#!/usr/bin/env python3
from sys import stderr, exit, stdout
import os

default_emulator="z80e-sdl -d TI84pSE"
default_debugger="z80e-sdl -d TI84pSE --debug"

if os.name == 'nt': # Windows
        default_emulator="wabbitemu"
        default_debugger="wabbitemu"

doc = """KnightOS SDK

Usage:
  knightos init [<name>]
        [--emulator=<emulator>]
        [--assembler=<assembler>]
        [--debugger=<debugger>]
        [--platform=<platform>]
        [--kernel-source=<path>]
  knightos install [--site-only] <packages>...
  knightos query <key>
  knightos -h | --help
  knightos --version

Options:
  init                      Initializes a new KnightOS project here or sets up an existing one
                            [name] is required when creating new projects.
  install                   Installs the specified packages
  query                     Queries the project's package.config for <key>. Useful for automation.
  --site-only               Installs the package but does not add it to package.config
  --assembler=<assembler>   Specifies an alternate assembler. [default: sass]
  --emulator=<emulator>     Specifies an alternate emulator. [default: {0}]
  --debugger=<debugger>     Specifies an alternate debugger. [default: {1}]
  --platform=<platform>     Specifies the calculator model to target. [default: TI84pSE]
                            Supported platforms are: TI73, TI83p, TI83pSE, TI84p, TI84pSE, TI84pCSE
  --kernel-source=<path>    Instead of downloading a kernel, compile one from <path>. Useful for testing kernels.
  -h --help                 Show this screen.
  --version                 Show version.
  

""".format(default_emulator, default_debugger)

from docopt import docopt
from init import execute as cmd_init
from install import execute as cmd_install
from query import execute as cmd_query

args = docopt(doc, version="1.2.0")

if args["--platform"]:
    if not args["--platform"] in [ "TI73", "TI83p", "TI83pSE", "TI84p", "TI84pSE", "TI84pCSE" ]:
        stderr.write("'{0}' is not a supported platform.\n".format(args["--platform"]))
        exit(1)

if args["init"]: cmd_init(project_name=args["<name>"], \
    assembler=args["--assembler"], emulator=args["--emulator"], debugger=args["--debugger"], \
    platform=args["--platform"], kernel_source=args["--kernel-source"])
if args["install"]: cmd_install(args["<packages>"], site_only=args["--site-only"])
if args["query"]: cmd_query(args["<key>"])
