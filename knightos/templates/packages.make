# This file is regenerated whenever you install new packages. Don't change it!

dependencies: {{#remote_packages}}__dependency__/{{repo}}/{{name}} {{/remote_packages}} {{#local_packages}} __dependency__/{{repo}}/{{name}} {{/local_packages}}
LIBRARIES={{#static_libs}}{{path}} {{/static_libs}}
.PHONY: {{#remote_packages}}__dependency__/{{repo}}/{{name}} {{/remote_packages}} {{#local_packages}} __dependency__/{{repo}}/{{name}} {{/local_packages}}

{{#remote_packages}}
__dependency__/{{repo}}/{{name}}:
	@kpack -e $(SDK)packages/{{name}}-{{version}}.pkg $(SDK)pkgroot/ > /dev/null
	@kpack -e -s $(SDK)packages/{{name}}-{{version}}.pkg $(SDK)pkgroot/ > /dev/null
	@mkdir -p $(SDK)include
	@cp -r $(SDK)pkgroot/include/* $(SDK)include/ ||:

{{/remote_packages}}

{{#local_packages}}
__dependency__/{{repo}}/{{name}}:
	@echo "Building local {{repo}}/{{name}}"
	@[ -d "{{path}}/.knightos" ] || { cd "{{path}}" && python -m knightos init; }
	cd "{{path}}" && make package
	cd "{{path}}" && make package
	@kpack -e {{path}}/{{name}}-*.pkg $(SDK)pkgroot/ > /dev/null
	@kpack -e -s {{path}}/{{name}}-*.pkg $(SDK)pkgroot/ > /dev/null
	@mkdir -p $(SDK)include
	@cp -r $(SDK)pkgroot/include/* $(SDK)include/ ||:

{{/local_packages}}
