.PHONY: setup setup-ui setup-playwright test test-verbose backend ui discovery-init discovery-list discovery-poll discovery-summary phase5-help

setup:
	python -m pip install -r requirements-dev.txt

setup-ui:
	npm install

setup-playwright:
	python -m playwright install chromium

test:
	pytest -q

test-verbose:
	pytest -vv

backend:
	python bridge_server.py

ui:
	npm run dev

discovery-init:
	python main.py init

discovery-list:
	python main.py list

discovery-poll:
	python main.py poll

discovery-summary:
	python main.py summary

phase5-help:
	python phase5_main.py --help
