# Project variables
TARGET_MODEL:=TI84pSE
AS:=sass
SDK=.knightos/
INCLUDE=$(SDK)include/;$(SDK)
ASFLAGS:=--encoding "Windows-1252" --include "$(INCLUDE)"
EMU:=wabbitemu
EMUFLAGS:=
GENKFS:=genkfs
KPACK:=kpack
.DEFAULT_GOAL=all

OUT:=bin/
ROOT:=$(OUT)root/
BIN:=$(ROOT)bin/
ETC:=$(ROOT)etc/
VAR:=$(ROOT)var/
SHARE:=$(ROOT)share/
