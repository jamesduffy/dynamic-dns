SHELL := /bin/bash


.PHONY: install
install:
	python -m pip install -r requirements.txt


.PHONY: run
run:
	FLASK_APP=ddns.py FLASK_ENV=development flask run
