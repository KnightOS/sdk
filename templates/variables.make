# Project variables
SDK=.knightos/
INCLUDE=$(SDK)include/;$(SDK)
AS:={{ assembler }}
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

OUT:=bin/
ROOT:=$(OUT)root/
BIN:=$(ROOT)bin/
ETC:=$(ROOT)etc/
VAR:=$(ROOT)var/
SHARE:=$(ROOT)share/
APPS:=$(VAR)applications/
