PREFIX:=/usr/
DESTDIR:=/usr/
.PHONY: install

install:
	mkdir -p $(DESTDIR)bin/
	mkdir -p $(DESTDIR)knightos-sdk/templates/
	install -c -m 775 *.py $(DESTDIR)knightos-sdk/
	install -c -m 775 templates/* $(DESTDIR)knightos-sdk/templates/
	echo -ne "#!/bin/sh\n/usr/bin/env python3 $(PREFIX)knightos-sdk/main.py \$$*" > $(DESTDIR)bin/knightos
	chmod +x $(DESTDIR)bin/knightos

uninstall:
	rm $(DESTDIR)bin/knightos
	rm -rf $(DESTDIR)knightos-sdk
