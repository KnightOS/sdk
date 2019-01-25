# KnightOS SDK targets
include $(SDK)packages.make

.PHONY: all run clean help info package includes dependencies

$(OUT)crt0.o: crt0.asm
	mkdir -p $(shell dirname $@)
	$(AS) $(INCLUDE) -c -o $(OUT)crt0.o crt0.asm

$(OUT)%.o: $(OUT)%.asm
	mkdir -p $(shell dirname $@)
	$(AS) $(INCLUDE) -c -o $@ $<

$(OUT)%.asm: %.c $(HEADERS)
	mkdir -p $(shell dirname $@)
	$(CC) $(INCLUDE) -S --std-c99 $< -o $@

all: {{#kernel_path}}kernel{{/kernel_path}} dependencies includes $(ALL_TARGETS)
	@rm -rf $(SDK)root
	@mkdir -p $(SDK)root
	@cp -r $(SDK)pkgroot/* $(SDK)root 2> /dev/null || true
	@rm -rf $(SDK)root/include
	@cp -r $(ROOT)* $(SDK)root/
	@cp $(SDK)kernel.rom $(SDK)debug.rom
	@mkdir -p $(SDK)root/etc
	@[ -e $(ETC)inittab ] || { echo "$(INIT)" > $(SDK)root/etc/inittab; }
	@$(GENKFS) $(SDK)debug.rom $(SDK)root/ > /dev/null

{{#kernel_path}}
kernel:
	$(MAKE) -C {{ kernel_path }} $(PLATFORM)
	cp {{ kernel_path }}/bin/include/kernel.inc $(SDK)include/
	cp {{ kernel_path }}/bin/include/kernel.h $(SDK)include/
{{/kernel_path}}

includes: dependencies
# If there are no includes to copy, suppress confusing "ignored error" message
	@-cp -r $(SDK)pkgroot/include/* $(SDK)include/ ||:

run: all
	$(EMU) $(SDK)debug.rom

debug: all
	$(DEBUGGER) $(SDK)debug.rom

clean:
	@rm -rf $(OUT)
	@rm -rf $(SDK)root
	@rm -rf $(SDK)debug.rom
	@rm -rf {{ project_name }}-$(VERSION).pkg

{{ project_name }}-$(VERSION).pkg: $(ALL_TARGETS)
	kpack {{ project_name }}-$(VERSION).pkg $(ROOT)
    
package: {{ project_name }}-$(VERSION).pkg

install: package
	kpack -e -s {{ project_name }}-$(VERSION).pkg $(PREFIX)
	
help:
	@echo "KnightOS Makefile for {{ project_name }}"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Common targets:"
	@echo "	all: 		Builds the entire project"
	@echo "	run: 		Builds and runs the project in the emulator"
	@echo "	debug: 		Builds and runs the project in the debugger"
	@echo "	package:	Builds a KnightOS package"
	@echo "	install:	Installs this package at the specified PREFIX"
	@echo "	info:		Lists information about this project"

info:
	@echo "Assembler:		$(AS)"
	@echo "Emulator:		$(EMU)"
	@echo "Include:		$(INCLUDE)"
	@echo "Platform:		$(PLATFORM)"
