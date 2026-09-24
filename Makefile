.PHONY: check test install uninstall

check: test

test:
	bash tests/test_install.sh

install:
	bash scripts/install.sh install

uninstall:
	bash scripts/install.sh uninstall
