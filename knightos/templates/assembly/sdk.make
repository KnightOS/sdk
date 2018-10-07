# KnightOS SDK targets
include $(SDK)packages.make

.PHONY: all run clean help info dependencies includes package{{#kernel_path}} kernel{{/kernel_path}}

all: {{#kernel_path}}kernel{{/kernel_path}} dependencies includes $(ALL_TARGETS)
	@rm -rf $(SDK)root
	@mkdir -p $(SDK)root
	@cp -R $(SDK)pkgroot/* $(SDK)root 2> /dev/null || true
	@rm -rf $(SDK)root/include
	@cp -R $(ROOT)* $(SDK)root/
	@cp $(SDK)kernel.rom $(SDK)debug.rom
	@mkdir -p $(SDK)root/etc
	@[ -e $(ETC)inittab ] || { echo "$(INIT)" > $(SDK)root/etc/inittab; }
	@$(GENKFS) $(SDK)debug.rom $(SDK)root/ > /dev/null

includes:
	@-cp -r $(SDK)pkgroot/include/* $(SDK)include/

{{#kernel_path}}
kernel:
	cd {{ kernel_path }} && make $(PLATFORM)
	cp {{ kernel_path }}/bin/include/kernel.inc $(SDK)include/
	cp {{ kernel_path }}/bin/include/kernel.h $(SDK)include/
{{/kernel_path}}

run: all
	$(EMU) $(SDK)debug.rom

debug: all
	$(DEBUGGER) $(SDK)debug.rom

clean:
	@rm -rf $(OUT)
	@rm -rf $(SDK)root
	@rm -rf $(SDK)debug.rom
	@rm -rf {{ project_name }}-$(VERSION).pkg

package: all
	kpack {{ project_name }}-$(VERSION).pkg $(ROOT)

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
