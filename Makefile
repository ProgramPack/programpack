SHELL := /usr/bin/env bash
.SILENT: sinstall stest sclean

sinstall:
	chmod +x setup.py
	./setup.py build
	pip3 install .
stest:
	chmod +x test/test.py
	python3 test/test.py
sclean:
	rm -rf *.egg-info
	rm -rf __pycache__