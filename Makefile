# start docker
docker-up:
	docker-compose up -d --build --wait

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
	pulumi destroy --yes && \
	# Don't delete the stack because we want to keep the yaml file
	rm -rf .pulumi

pytest:
	pulumi --cwd pulumi stack select local && \
	export LAMBDA_URL=$$(pulumi --cwd pulumi stack output lambda_url) && \
	uv run pytest
