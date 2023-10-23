SHELL=/bin/bash -o pipefail
BUILD_PRINT = STEP: 

CURRENT_UID := $(shell id -u)
export CURRENT_UID
#project name that will be used as a prefix on docker containers
#this is important for the nginx configuration
PROJECT = lr
# include .env files if they exist
-include ./infra/notebook/.env.test
-include .env


#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------

install:
	@ echo "$(BUILD_PRINT)Installing the prod requirements"
	@ pip install --upgrade pip
	@ pip install -r requirements.txt

install-dev: install-test
	@ echo "$(BUILD_PRINT)Installing the dev requirements"
	@ pip install --upgrade pip
	@ pip install -r requirements-dev.txt

#install:
#	@ echo "$(BUILD_PRINT)Installing the requirements"
#	@ echo "$(BUILD_PRINT)Warning: this setup depends on the Airflow 2.1 constraints. If you upgrade the Airflow version, make sure to adjust the constraint file reference."
#	@ pip install --upgrade pip
#	@ pip install "apache-airflow==2.1.0" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2-1/constraints-no-providers-3.8.txt"
##	@ pip install -r requirements.txt --use-deprecated legacy-resolver --constraint "https://github.com/apache/airflow/blob/constraints-2-1/constraints-no-providers-3.8.txt"
#	@ pip install -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2-1/constraints-no-providers-3.8.txt"
#	@ python -m spacy download en_core_web_sm
#
#all: install

test:
	@ echo "$(BUILD_PRINT)Running the unit tests (default)"
	@ py.test --ignore=tests/tests/e2e -s --html=report.html --self-contained-html

test-e2e:
	@ echo "$(BUILD_PRINT)Running the end to end tests"
	@ py.test --ignore=tests/tests/unit -s --html=report.html --self-contained-html

test-all:
	@ echo "$(BUILD_PRINT)Running all tests"
	@ py.test -s --html=report.html --self-contained-html



# Getting secrets from Vault

# Testing whether an env variable is set or not
guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "$(BUILD_PRINT)Environment variable $* not set"; \
        exit 1; \
	fi

# Testing that vault is installed
vault-installed: #; @which vault1 > /dev/null
	@ if ! hash vault 2>/dev/null; then \
        echo "$(BUILD_PRINT)Vault is not installed, refer to https://www.vaultproject.io/downloads"; \
        exit 1; \
	fi

# Get secrets in dotenv format
vault_secret_to_dotenv: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
	@ echo "$(BUILD_PRINT)Writing the lr secret from Vault to .env"

	@ vault kv get -format="json" lr/notebook | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" lr/haystack | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" lr/graphdb| jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" lr/minio | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" lr/elastic-search | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" lr/vault | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env

# Get secrets in json format
vault_secret_to_json: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
	@ echo "$(BUILD_PRINT)Writing the lr/sem-covid secret from Vault to variables.json"
	@ vault kv get -format="json" lr/notebook | jq -r ".data.data" > tmp1.json
	@ vault kv get -format="json" lr/haystack | jq -r ".data.data" > tmp2.json
	@ vault kv get -format="json" lr/graphdb | jq -r ".data.data" > tmp3.json
	@ vault kv get -format="json" lr/minio | jq -r ".data.data" > tmp4.json
	@ vault kv get -format="json" lr/elastic-search | jq -r ".data.data" > tmp5.json
	@ vault kv get -format="json" lr/vault | jq -r ".data.data" > tmp6.json
	@ jq -s '.[0] * .[1] * .[2] * .[3] * .[4] * .[5]' tmp*.json> variables.json
	@ rm tmp*.json




lint:
	@ echo "$(BUILD_PRINT)Looking for dragons in your code ...."
	@ pylint legal-radar


build-externals:
	@ echo "$(BUILD_PRINT)Creating the necessary volumes, networks and folders and setting the special rights"
	@ docker network create proxy-net || true

create-env-airflow:
	@ echo "$(BUILD_PRINT) Create Airflow env"
	@ mkdir -p infra/airflow/logs infra/airflow/plugins
	@ cd infra/airflow/ && ln -s -f ../../dags && ln -s -f ../../legal_radar
	@ echo -e "AIRFLOW_UID=$(CURRENT_UID)" >infra/airflow/.env

build-airflow: create-env-airflow build-externals
	@ echo "$(BUILD_PRINT) Build Airflow services"
	@ docker-compose -p ${PROJECT} --file ./infra/airflow/docker-compose.yaml --env-file .env build --no-cache --force-rm
	@ docker-compose -p ${PROJECT} --file ./infra/airflow/docker-compose.yaml --env-file .env up -d --force-recreate

start-airflow: build-externals
	@ echo "$(BUILD_PRINT)Starting Airflow servies"
	@ docker-compose -p ${PROJECT} --file ./infra/airflow/docker-compose.yaml --env-file .env up -d

stop-airflow:
	@ echo "$(BUILD_PRINT)Stoping Airflow services"
	@ docker-compose -p ${PROJECT} --file ./infra/airflow/docker-compose.yaml --env-file .env down

build-elasticsearch: build-externals
	@ echo "$(BUILD_PRINT) Build Elasticsearch services"
	@ docker-compose -p ${PROJECT} --file ./infra/elasticsearch/docker-compose.yml --env-file .env build --no-cache --force-rm
	@ docker-compose -p ${PROJECT} --file ./infra/elasticsearch/docker-compose.yml --env-file .env up -d --force-recreate

start-elasticsearch: build-externals
	@ echo "$(BUILD_PRINT)Starting the Elasticsearch services"
	@ docker-compose -p ${PROJECT} --file ./infra/elasticsearch/docker-compose.yml --env-file .env up -d

stop-elasticsearch:
	@ echo "$(BUILD_PRINT)Stopping the Elasticsearch services"
	@ docker-compose -p ${PROJECT} --file ./infra/elasticsearch/docker-compose.yml --env-file .env down

start-storage: build-externals
	@ echo "$(BUILD_PRINT)Starting the File Storage services"
	@ docker-compose -p ${PROJECT} -p ${PROJECT} --file ./infra/storage/docker-compose.yml --env-file .env up -d

stop-storage:
	@ echo "$(BUILD_PRINT)Stopping the File Storage services"
	@ docker-compose -p ${PROJECT} -p ${PROJECT} --file ./infra/storage/docker-compose.yml --env-file .env down

start-notebook-cuda: build-externals
	@ echo "$(BUILD_PRINT)Starting the Jupyter Notebook services"
	@ docker image build -t notebook_meaningfy_lr:latest -f infra/notebook/Dockerfile ./infra/notebook
	@ docker run --gpus all -d -it -p 8890:8888 -v jupyter-notebook-work-lr:/home/jovyan/work \
			-e JUPYTER_ENABLE_LAB=yes \
			--restart unless-stopped \
			--name notebook_meaningfy \
			cschranz/gpu-jupyter:v1.4_cuda-11.0_ubuntu-20.04 \
			start-notebook.sh \
            --NotebookApp.password=${JUPYTER_PASSWORD} \
            --NotebookApp.token=${JUPYTER_TOKEN} \
#	@ docker-compose --file ./infra/notebook-cuda/docker-compose.yml --env-file .env up -d

stop-notebook-cuda:
	@ echo "$(BUILD_PRINT)Starting the Jupyter Notebook services"
	@ docker stop notebook_meaningfy
	@ docker rm notebook_meaningfy
#	@ docker-compose --file ./infra/notebook-cuda/docker-compose.yml --env-file .env down


build-jupyterhub:
	@ echo "$(BUILD_PRINT)Building Jupyterhub servies"
	@ docker-compose -p ${PROJECT} --file ./infra/jupyterhub/docker-compose.yml build --no-cache --force-rm
	@ docker-compose -p ${PROJECT} --file ./infra/jupyterhub/docker-compose.yml up -d --force-recreate

start-jupyterhub:
	@ echo "$(BUILD_PRINT)Starting Jupyterhub servies"
	@ docker-compose -p ${PROJECT} --file ./infra/jupyterhub/docker-compose.yml up -d

stop-jupyterhub:
	@ echo "$(BUILD_PRINT)Stoping Jupyterhub servies"
	@ docker-compose -p ${PROJECT} --file ./infra/jupyterhub/docker-compose.yml down

create-env-semantic-search:
	@ echo "$(BUILD_PRINT) Create semantic-search env"
	@ cd infra/semantic-search/ && cp -r ../../legal_radar .

start-semantic-search-build: create-env-semantic-search
	@ echo "$(BUILD_PRINT)Starting the semantic-search services"
	@ docker-compose -p ${PROJECT} --file ./infra/semantic-search/docker-compose.yml --env-file .env build --no-cache --force-rm
	@ docker-compose -p ${PROJECT} --file ./infra/semantic-search/docker-compose.yml --env-file .env up -d --force-recreate

stop-semantic-search: create-env-semantic-search
	@ echo "$(BUILD_PRINT)Stopping the semantic-search services"
	@ docker-compose -p ${PROJECT} --file ./infra/semantic-search/docker-compose.yml --env-file .env down


start-notebook: build-externals
	@ echo "$(BUILD_PRINT)Starting the Jupyter Notebook services"
	@ docker-compose -p ${PROJECT} --file ./infra/notebook/docker-compose.yml --env-file .env up -d

start-notebook-build: build-externals
	@ echo "$(BUILD_PRINT)Rebuildig the image and then starting the Jupyter Notebook services"
	@ docker-compose -p ${PROJECT} --file ./infra/notebook/docker-compose.yml --env-file .env build --no-cache --force-rm
	@ docker-compose -p ${PROJECT} --file ./infra/notebook/docker-compose.yml --env-file .env up -d --force-recreate

stop-notebook:
	@ echo "$(BUILD_PRINT)Stopping the Jupyter Notebook services"
	@ docker-compose -p ${PROJECT} --file ./infra/notebook/docker-compose.yml --env-file .env down


update-project:
	@ echo "$(BUILD_PRINT)Sync project files from git repository."
	@ git pull

start-services: | start-airflow start-elasticsearch start-jupyterhub start-notebook start-storage start-semantic-search-build
stop-services: | stop-airflow stop-elasticsearch stop-jupyterhub stop-notebook stop-storage stop-semantic-search-build
