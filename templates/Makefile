include .knightos/variables.make

# This is a list of files that need to be added to the filesystem when installing your program
ALL_TARGETS:=$(BIN){{ project_name }}

# This is all the make targets to produce said files
$(BIN){{ project_name }}: main.asm
	mkdir -p $(BIN)
	$(AS) $(ASFLAGS) --listing $(OUT)main.list main.asm $(BIN){{ project_name }}

include .knightos/sdk.make
