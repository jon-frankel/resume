### ---------------------------------------------------------
### This is the Makefile for managing local development.
### Below are the available commands and their descriptions.
### ---------------------------------------------------------

# Attributions: https://stackoverflow.com/a/47107132 and https://stackoverflow.com/a/64996042
help: ## Show this help.
	@sed -ne '/@sed/!s/### //p' $(MAKEFILE_LIST)
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install system and app dependencies
	brew --version || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	docker compose version || brew install --cask orbstack
	nvm --version || brew install nvm
	nvm install && nvm use && npm install -g pnpm
	uv --version || brew install uv
	uv python install
	pulumi version || brew install pulumi/tap/pulumi
	pnpm install
	uv sync --locked --all-extras --dev

docker-up: ## Start ministack in docker
	docker compose up -d --build --wait

docker-destroy: ## Stop and remove ministack
	docker compose down
	docker compose rm ministack

pulumi-up: ## Deploy pulumi stack to ministack
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

launch: docker-up pulumi-up ## Bring Docker and Pulumi up and launch the app
	@echo "App is running at http://resume-local.frankel.test.s3-website.localhost:4566/index.html 🚀"
	@open http://resume-local.frankel.test.s3-website.localhost:4566/index.html

destroy: pulumi-destroy docker-destroy ## Gracefully destroy all resources
	@echo "Destroyed all resources 💥"

start-dev: ## Start the front end app dev server
	cd pulumi && \
	export PULUMI_CONFIG_PASSPHRASE=local && \
	export PULUMI_BACKEND_URL=file://.pulumi && \
	pulumi login --local && \
	pulumi stack select local && \
	export LAMBDA_URL=$$(pulumi stack output lambda_url) && \
	echo $$LAMBDA_URL && \
	cd .. && \
	pnpm start

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

playwright: ## Run end-to-end tests
	pnpm exec playwright test

test: pytest playwright ## Run all tests
