# This file is regenerated whenever you install new packages. Don't change it!

dependencies: {{#packages}}__dependency__/{{repo}}/{{name}} {{/packages}}

.PHONY: {{#packages}}__dependency__/{{repo}}/{{name}} {{/packages}}

{{#packages}}
__dependency__/{{repo}}/{{name}}:
	@kpack -e $(SDK)packages/{{filename}} $(SDK)pkgroot/ > /dev/null
	@kpack -e -s $(SDK)packages/{{filename}} $(SDK)pkgroot/ > /dev/null
	@cp -r $(SDK)pkgroot/include/* $(SDK)include/ ||:

{{/packages}}
