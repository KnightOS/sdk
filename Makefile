PREFIX:=usr
.PHONY: install

install:
	mkdir -p $(PREFIX)bin/
	mkdir -p $(PREFIX)knightos-sdk/templates/
	install -c -m 775 *.py $(PREFIX)knightos-sdk/
	install -c -m 775 templates/* $(PREFIX)knightos-sdk/templates/
	echo -ne "#!/bin/sh\n/usr/bin/env python3 $(PREFIX)knightos-sdk/main.py \$$*" > $(PREFIX)bin/knightos
	chmod +x $(PREFIX)bin/knightos

uninstall:
	rm $(PREFIX)bin/knightos
	rm -rf $(PREFIX)knightos-sdk
