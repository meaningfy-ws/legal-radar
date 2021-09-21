SHELL=/bin/bash -o pipefail
BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------


install:
	@ echo "$(BUILD_PRINT)Installing the requirements"
	@ echo "$(BUILD_PRINT)Warning: this setup depends on the Airflow 2.1 constraints. If you upgrade the Airflow version, make sure to adjust the constraint file reference."
	@ pip install --upgrade pip
	@ pip install "apache-airflow==2.1.0" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2-1/constraints-no-providers-3.8.txt"
#	@ pip install -r requirements.txt --use-deprecated legacy-resolver --constraint "https://github.com/apache/airflow/blob/constraints-2-1/constraints-no-providers-3.8.txt"
	@ pip install -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2-1/constraints-no-providers-3.8.txt"
	@ python -m spacy download en_core_web_sm

all: install

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
	@ pylint sem_covid


build-externals:
	@ echo "$(BUILD_PRINT)Creating the necessary volumes, networks and folders and setting the special rights"
	@ docker volume create s3-disk-lr
	@ docker volume create jupyter-notebook-work-lr
	@ docker volume create elasticsearch-lr
	@ docker volume create graphdb-data-lr
	@ docker network create -d bridge lr || true


start-storage: build-externals
	@ echo "$(BUILD_PRINT)Starting the File Storage services"
# 	@ docker-compose --file ./infra/storage/docker-compose.yml --env-file infra/storage/.env.test up -d
	@ docker-compose --file ./infra/storage/docker-compose.yml --env-file .env up -d

stop-storage:
	@ echo "$(BUILD_PRINT)Stopping the File Storage services"
# 	@ docker-compose --file ./infra/storage/docker-compose.yml --env-file infra/storage/.env.test down
	@ docker-compose --file ./infra/storage/docker-compose.yml --env-file .env down

start-notebook: build-externals
	@ echo "$(BUILD_PRINT)Starting the Jupyter Notebook services"
	@ docker-compose --file ./infra/notebook/docker-compose.yml --env-file infra/notebook/.env.test up -d
#	@ docker-compose --file ./infra/notebook/docker-compose.yml --env-file .env up -d

stop-notebook:
	@ echo "$(BUILD_PRINT)Starting the Jupyter Notebook services"
	@ docker-compose --file ./infra/notebook/docker-compose.yml --env-file infra/notebook/.env.test down
#	@ docker-compose --file ./infra/notebook/docker-compose.yml --env-file .env down

start-haystack: build-externals
	@ echo "$(BUILD_PRINT)Starting the Haystack services"
# 	@ docker-compose --file ./infra/haystack/docker-compose.yml --env-file infra/haystack/.env.test up -d
	@ docker-compose --file ./infra/haystack/docker-compose.yml --env-file .env up -d

stop-haystack:
	@ echo "$(BUILD_PRINT)Starting the Haystack services"
# 	@ docker-compose --file ./infra/haystack/docker-compose.yml --env-file infra/haystack/.env.test down
	@ docker-compose --file ./infra/haystack/docker-compose.yml --env-file .env down

start-elasticsearch: build-externals
	@ echo "$(BUILD_PRINT)Starting the Elasticsearch services"
# 	@ docker-compose --file ./infra/elasticsearch/docker-compose.yml --env-file infra/elasticsearch/.env.test up -d
	@ docker-compose --file ./infra/elasticsearch/docker-compose.yml --env-file .env up -d

stop-elasticsearch:
	@ echo "$(BUILD_PRINT)Stopping the Elasticsearch services"
# 	@ docker-compose --file ./infra/elasticsearch/docker-compose.yml --env-file infra/elasticsearch/.env.test down
	@ docker-compose --file ./infra/elasticsearch/docker-compose.yml --env-file .env down

start-graphdb: build-externals
	@ echo "$(BUILD_PRINT)Starting the Graphdb services"
# 	@ docker-compose --file ./infra/graphdb/docker-compose.yml --env-file infra/graphdb/.env.test up -d
	@ docker-compose --file ./infra/graphdb/docker-compose.yml --env-file .env up -d

stop-graphdb:
	@ echo "$(BUILD_PRINT)Stopping the Graphdb services"
# 	@ docker-compose --file ./infra/graphdb/docker-compose.yml --env-file infra/graphdb/.env.test down
	@ docker-compose --file ./infra/graphdb/docker-compose.yml --env-file .env down