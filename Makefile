VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

# include .env
# export $(shell sed 's/=.*//' .env)

# ifneq (,$(wildcard ./.env.bak))
#     include .env.bak
#     export
# endif

serve-dev: $(VENV)/bin/activate
	$(VENV)/bin/flask db migrate
	$(VENV)/bin/flask db upgrade
	$(PYTHON) app.py

serve-prod: $(VENV)/bin/activate
	 $(VENV)/bin/flask db migrate
	 $(VENV)/bin/flask db upgrade
	 $(VENV)/bin/gunicorn -c gunicorn-config.py app:app

migrate: $(VENV)/bin/activate
	 $(VENV)/bin/flask db migrate
	 $(VENV)/bin/flask db upgrade

test: $(VENV)/bin/activate
	 $(VENV)/bin/pytest tests/ -v

venv/bin/activate: requirements.txt
				   python3 -m venv venv
				   $(PIP) install -r requirements.txt
clean:
	rm -rf __pycache__
	rm -rf venv