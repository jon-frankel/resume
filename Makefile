# start docker
docker-up:
	docker compose up -d --build --wait

docker-destroy:
	docker compose down
	docker compose rm localstack
	rm -rf .localstack

pulumi-up:
	cd pulumi && \
	export PULUMI_CONFIG_PASSPHRASE=local && \
	export PULUMI_BACKEND_URL=file://.pulumi && \
	mkdir -p .pulumi && \
	pulumi login --local && \
	pulumi stack select -c local && \
	pulumi up --yes

pulumi-destroy:
	cd pulumi && \
	export PULUMI_CONFIG_PASSPHRASE=local && \
	export PULUMI_BACKEND_URL=file://.pulumi && \
	pulumi login --local && \
	pulumi stack select local && \
	(pulumi destroy --yes || echo "already destroyed?")  && \
	rm -rf .pulumi
	# Don't do pulumi stack delete because we want to keep the yaml file

pytest:
	cd pulumi && \
	export PULUMI_CONFIG_PASSPHRASE=local && \
	export PULUMI_BACKEND_URL=file://.pulumi && \
	pulumi login --local && \
	pulumi stack select local && \
	export LAMBDA_URL=$$(pulumi stack output lambda_url) && \
	echo $$LAMBDA_URL && \
	cd .. && \
	uv run pytest
