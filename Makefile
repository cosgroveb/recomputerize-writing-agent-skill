PYTHON ?= python3

.PHONY: check test install uninstall

check:
	$(PYTHON) scripts/check.py
	$(MAKE) test

test:
	$(PYTHON) -m unittest discover -s tests -v

install:
	$(PYTHON) scripts/install.py install

uninstall:
	$(PYTHON) scripts/install.py uninstall
