prefix:=/usr/local
bindir:=$(prefix)/bin
libdir:=$(prefix)/lib
.PHONY: install

all: knightos.sh

knightos.sh:
	printf '#!/bin/sh\n/usr/bin/env python3 "$(prefix)/lib/knightos-sdk/main.py" "$$@"\n' > knightos.sh

install: all
	mkdir -p "$(bindir)/"
	mkdir -p "$(libdir)/knightos-sdk/templates/assembly/"
	mkdir -p "$(libdir)/knightos-sdk/templates/c/"
	install -c -m 775 *.py "$(libdir)/knightos-sdk/"
	install -c -m 775 templates/assembly/* "$(libdir)/knightos-sdk/templates/assembly/"
	install -c -m 775 templates/c/* "$(libdir)/knightos-sdk/templates/c/"
	install -c -m 775 templates/packages.make "$(libdir)/knightos-sdk/templates/packages.make"
	install -c -m 775 knightos.sh "$(bindir)/knightos"

uninstall:
	rm "$(bindir)/knightos"
	rm -rf "$(libdir)/knightos-sdk"

clean:
	rm knightos.sh
