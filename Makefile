PREFIX:=/usr/
DESTDIR:=/usr/
.PHONY: install

install:
	mkdir -p $(DESTDIR)bin/
	mkdir -p $(DESTDIR)knightos-sdk/templates/assembly/
	mkdir -p $(DESTDIR)knightos-sdk/templates/c/
	install -c -m 775 *.py $(DESTDIR)knightos-sdk/
	install -c -m 775 templates/assembly/* $(DESTDIR)knightos-sdk/templates/assembly/
	install -c -m 775 templates/c/* $(DESTDIR)knightos-sdk/templates/c/
	echo -ne "#!/bin/sh\n/usr/bin/env python3 $(PREFIX)knightos-sdk/main.py \$$*" > $(DESTDIR)bin/knightos
	chmod +x $(DESTDIR)bin/knightos

uninstall:
	rm $(DESTDIR)bin/knightos
	rm -rf $(DESTDIR)knightos-sdk
