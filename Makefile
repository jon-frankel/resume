### ---------------------------------------------------------
### This is the Makefile for the project.
### Below are the available commands and their descriptions.
### ---------------------------------------------------------

# Attributions: https://stackoverflow.com/a/47107132 and https://stackoverflow.com/a/64996042
help: ## Show this help.
	@sed -ne '/@sed/!s/### //p' $(MAKEFILE_LIST)
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

docker-up: ## Start localstack in docker
	docker compose up -d --build --wait

docker-destroy: ## Stop and remove localstack
	docker compose down
	docker compose rm localstack
	rm -rf .localstack

pulumi-up: ## Deploy pulumi stack to localstack
	cd pulumi && \
	export PULUMI_CONFIG_PASSPHRASE=local && \
	export PULUMI_BACKEND_URL=file://.pulumi && \
	mkdir -p .pulumi && \
	pulumi login --local && \
	pulumi stack select -c local && \
	pulumi up --yes

pulumi-destroy: ## Destroy pulumi stack
	cd pulumi && \
	export PULUMI_CONFIG_PASSPHRASE=local && \
	export PULUMI_BACKEND_URL=file://.pulumi && \
	pulumi login --local && \
	pulumi stack select local && \
	(pulumi destroy --yes || echo "already destroyed?")  && \
	rm -rf .pulumi
	# Don't do pulumi stack delete because we want to keep the yaml file

pytest: ## Run integration tests
	cd pulumi && \
	export PULUMI_CONFIG_PASSPHRASE=local && \
	export PULUMI_BACKEND_URL=file://.pulumi && \
	pulumi login --local && \
	pulumi stack select local && \
	export LAMBDA_URL=$$(pulumi stack output lambda_url) && \
	echo $$LAMBDA_URL && \
	cd .. && \
	uv run pytest
