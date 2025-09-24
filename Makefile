VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
# COMMIT_ID:= $(git rev-parse HEAD | cut -c -8)
COMMIT_ID != git rev-parse HEAD | cut -c -8
DOCKER_USERNAME ?= harsh18262one2n
DOCKER_REGISTRY := $(DOCKER_USERNAME)/student-api
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
	 $(VENV)/bin/pytest test/ -v

lint: 
	ruff check --fix

docker-build: 
	docker build . -t $(DOCKER_REGISTRY):$(COMMIT_ID)


serve-docker: 
# 	docker run --rm -p 5000:5000 -v .env:/app/.env $(DOCKER_REGISTRY):$(COMMIT_ID)
# 	docker compose up db
# 	docker run -v instance:/app/instance -v .env:/app/.env student-api:$(COMMIT_ID) flask db migrate
# 	docker run -v instance:/app/instance -v .env:/app/.env student-api:$(COMMIT_ID) flask db upgrade
	docker compose up -d
serve-vagrant: 
	vagrant up --provider=virtualbox --provision

docker-push:
	docker push $(DOCKER_REGISTRY):$(COMMIT_ID)

docker-stop:
	docker compose down
	
venv/bin/activate: requirements.txt
				   python3 -m venv venv
				   $(PIP) install -r requirements.txt

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf .pytest_cache
	minikube delete
	docker compose down --rmi all --remove-orphans

minikube-setup:
	minikube start -n 4
	kubectl label node minikube-m02 type=application
	kubectl label node minikube-m03 type=database
	kubectl label node minikube-m04 type=dependent_services

minikube-stop:
	minikube stop

minikube-start:
	minikube start -n 4

minikube-deploy:
	cd $(CURDIR)/k8s/scripts;sh helm.sh
	cd $(CURDIR)/k8s;kubectl apply -f ./dependent-service.yaml;kubectl apply -f ./database.yaml;kubectl apply -f ./application.yaml;