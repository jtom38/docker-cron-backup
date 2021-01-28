.PHONY: help
help: ## Shows this help command
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Builds the docker image
	docker build -t cron-backup .

test: ## Runs the docker image in temp space
	docker run -it \
		-v ${PWD}/demo/source:/source \
		-v ${PWD}/demo/backup:/backup \
		--env-file ./.env \
		cron-backup:latest \
		python3 /scripts/backup.py

setup-test:
	mkdir ./demo/
	mkdir ./demo/source
	mkdir ./demo/backup
	cp env .env
	echo "This is a test document that we will backup." > ./demo/source/placeholder