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
	venv/bin/python3 app.py

serve-prod: $(VENV)/bin/activate
	 $(VENV)/bin/flask db migrate
	 $(VENV)/bin/flask db upgrade
	 venv/bin/gunicorn -c gunicorn-config.py app:app

venv/bin/activate: requirements.txt
				   python3 -m venv venv
				   venv/bin/pip install -r requirements.txt

clean:
	rm -rf __pycache__
	rm -rf venv