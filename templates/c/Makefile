include .knightos/variables.make

#INCLUDE+=add to your include path

HEADERS:=$(wildcard *.h)

ALL_TARGETS:=$(BIN){{ project_name }}

$(BIN){{ project_name }}: $(OUT)main.o $(OUT)crt0.o
	mkdir -p $(BIN)
	scas -fauto-relocation $(LIBRARIES) $(OUT)main.o -o $(BIN){{ project_name }}

include .knightos/sdk.make
