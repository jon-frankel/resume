# Jon Frankel's Extremely Overengineered Résumé

This repo holds my résumé, motivated by the [Cloud Resume Challenge](https://cloudresumechallenge.dev).
It's purposefully overengineered to demonstrate the skillset needed for a full-stack, cloud-based app.
You can find the live production deployment [here](https://resume.frankel.dev).

## The Résumé

The résumé itself is built mostly in plain-old [HTML](public/index.html) and [CSS](public/style.css).
There is a small bit of JavaScript to display the visit counter (located at the bottom of the page).
The JavaScript is written in [TypeScript](src/index.ts) and compiled with [Webpack](webpack.config.ts)
into a single file in the `public` directory, next to the manually written HTML and CSS.

All the static content is hosted on AWS S3.

## The API

There is a single endpoint, [written in Python](api/main.py), to support a visit counter.
That endpoint increments the counter for each request and returns the current value.
The API is deployed on AWS Lambda.

## The Database

The Python API uses DynamoDB to store the visit counter. Right now there is only a single global
counter.

## Infrastructure as Code

The infrastructure is defined in [Pulumi](pulumi/__main__.py). This includes AWS resources:
 - The S3 bucket for hosting the static content
 - The DynamoDB table for the counter
 - The Lambda function for the API
 - The IAM roles and policies for the Lambda function

## DNS

Unlike the other infrastructure that is maintained by Pulumi and deployed to AWS,
DNS is managed manually in Cloudflare. This is because I have other records on the frankel.dev 
domain (e.g., email), so I don't want to mix IaC control for this project with unrelated DNS records.
A more minor reason is that Cloudflare has a free tier for DNS management, unlike AWS Route 53.

## Local Development

To support local versions of S3, DynamoDB, and Lambda, this project uses MiniStack running
[inside Docker](docker-compose.yml). The same Pulumi that deploys to AWS also deploys to MiniStack,
just with a [different YAML config file](pulumi/Pulumi.local.yaml).

If you want to run the project locally yourself, you can use the [Makefile](Makefile). Use `make help`
to see all the available commands. For a quickstart, do:

```bash
make install
make launch
```

This will start MiniStack and deploy via Pulumi. Use `make destroy` to tear everything down.

## Tests

Python integration tests use [Pytest](api/integration_tests/test_main.py).
There are also Playwright [end-to-end tests](e2e/index.spec.ts) to validate the UI.

Both test suites depend on the app running locally in MiniStack.

## CI/CD

Pull requests require tests to pass before they can be merged. The [test workflow](.github/workflows/test.yml)
uses Pulumi to deploy the app to MiniStack and runs the integration and end-to-end tests. There is also
an integration between Pulumi and GitHub that previews changes to the staging environment.

Merging into develop triggers a deployment to the staging environment, which is managed in Pulumi. The
[deployment workflow](.github/workflows/deployment.yml) then triggers a smoke test, which is just
the end-to-end tests running against the deployment in AWS. The same thing happens for merging into main,
but against the production environment.

## AWS Setup

The easy way to deploy to AWS would be to use a single login with a single AWS account,
and store credentials in secrets. But this is meant to be an exercise in overengineering,
so the AWS setup is as follows:

 - A single root login (password and MFA) for managing the top-level AWS account.
 - Separate accounts in organizational units for staging and production environments.
 - A separate IAM user for each OU with admin access to the account in that OU.
 - Logging in to the console for each environment requires Okta Single Sign-On (SSO).
 - Each AWS environment is integrated with a separate Pulumi stack via OpendID Connect.
 - The Pulumi staging stack receives webhooks from Github for merges into develop,
   which then deploys to the AWS Staging OU.
 - The Pulumi production stack receives webhooks from Github for merges into main,
   which then deploys to the AWS Production OU.

### References:

 - [Pulumi Github App](https://www.pulumi.com/docs/iac/guides/continuous-delivery/github-app/)
 - [OpenID Connect for AWS with Pulumi](https://www.pulumi.com/docs/deployments/deployments/oidc/aws)
 - [Configure SAML and SCIM with Okta and IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/gs-okta.html)
