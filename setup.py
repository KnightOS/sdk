#!/usr/bin/env python3
from distutils.core import setup
import subprocess
import glob
import os

ver = os.environ.get("PKGVER") or subprocess.run(['git', 'describe', '--tags'],
      stdout=subprocess.PIPE).stdout.decode().strip()

setup(
  name = 'knightos',
  packages = ['knightos', 'knightos.commands'],
  version = ver,
  description = 'KnightOS SDK',
  author = 'Drew DeVault',
  author_email = 'sir@cmpwn.com',
  url = 'https://github.com/KnightOS/sdk',
  install_requires = ['requests', 'yaml', 'pystache', 'docopt'],
  license = 'AGPL-3.0',
  scripts=['bin/knightos'],
  package_data={
      'knightos': [
          'templates/*',
          'templates/c/*',
          'templates/assembly/*',
      ]
  },
)
