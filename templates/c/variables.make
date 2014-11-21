# Project variables
SDK=.knightos/
INCLUDE=$(SDK)include/;$(SDK)
AS:={{ assembler }}
CC:={{ compiler }}
EMU:={{ emulator }}
DEBUGGER:={{ debugger }}
ASFLAGS:=--encoding "Windows-1252" --include "$(INCLUDE)"
GENKFS:=genkfs
KPACK:=kpack
.DEFAULT_GOAL=all
INIT:=/bin/{{ project_name }}
VERSION:=$(shell knightos query version)
PLATFORM:={{ platform }}
KEY:={{ key }}
UPGRADEEXT:={{ upgrade_ext }}
PRIVILEGED:={{ privileged }}
FAT:={{ fat }}

LIBC:=$(SDK)pkgroot/lib/c

OUT:=bin/
ROOT:=$(OUT)root/
BIN:=$(ROOT)bin/
LIB:=$(ROOT)lib/
ETC:=$(ROOT)etc/
VAR:=$(ROOT)var/
INC:=$(ROOT)include/
SHARE:=$(ROOT)share/
APPS:=$(VAR)applications/
