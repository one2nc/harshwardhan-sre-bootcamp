VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
# COMMIT_ID:= $(git rev-parse HEAD | cut -c -8)
COMMIT_ID != git rev-parse HEAD | cut -c -8

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

build: 
	docker build . -t student-api:$(COMMIT_ID)

serve-prod: $(VENV)/bin/activate
	 $(VENV)/bin/flask db migrate
	 $(VENV)/bin/flask db upgrade
	 $(VENV)/bin/gunicorn -c gunicorn-config.py app:app

serve-docker: 
	docker run --rm -p 5000:5000 -v .env:/app/.env student-api:$(COMMIT_ID)

venv/bin/activate: requirements.txt
				   python3 -m venv venv
				   $(PIP) install -r requirements.txt
				   docker build . -t student-api:$(COMMIT_ID)

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf .pytest_cache