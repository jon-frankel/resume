import mimetypes
import os

import pulumi_archive as archive
import pulumi_aws as aws

import pulumi

stack_config = pulumi.Config()
target_domain = stack_config.require("targetDomain")
lambda_name = "web-counter-lambda"

# Lambda role
assume_role = aws.iam.get_policy_document(
    statements=[
        {
            "effect": "Allow",
            "principals": [{"identifiers": ["lambda.amazonaws.com"], "type": "Service"}],
            "actions": ["sts:AssumeRole"],
        }
    ]
)
lambda_role = aws.iam.Role(
    f"{lambda_name}-role",
    name=f"{lambda_name}-role",
    assume_role_policy=assume_role.json,
)

# Lambda logging permissions
log_group = aws.cloudwatch.LogGroup(
    f"{lambda_name}-log-group",
    name=f"/aws/lambda/{lambda_name}",
    retention_in_days=14
)
log_policy_doc = aws.iam.get_policy_document(statements=[{
    "effect": "Allow",
    "actions": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
    ],
    "resources": ["arn:aws:logs:*:*:*"],
}])
log_policy = aws.iam.Policy(
    f"{lambda_name}-log-policy",
    name=f"{lambda_name}-log-policy",
    path="/",
    description="IAM policy for lambda to write logs",
    policy=log_policy_doc.json,
)
log_policy_attachment = aws.iam.RolePolicyAttachment(
    f"{lambda_name}-log-policy-attachment",
    role=lambda_role.name,
    policy_arn=log_policy.arn,
)

# DynamoDB table for visit counter
visits_table = aws.dynamodb.Table("visits-counter",
    name="visits-counter",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="updated_at",
            type="N",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="visits",
            type="N",
        ),
    ],
    billing_mode="PAY_PER_REQUEST",
    hash_key="id",
    global_secondary_indexes=[
        aws.dynamodb.TableGlobalSecondaryIndexArgs(
            name="updated_at-index",
            hash_key="updated_at",
            projection_type="ALL",
        ),
        aws.dynamodb.TableGlobalSecondaryIndexArgs(
            name="visits-index",
            hash_key="visits",
            projection_type="ALL",
        ),
    ],
    ttl={
        "attribute_name": "ttl",
        "enabled": False,
    }
)

# Add DynamoDB permissions to Lambda role
dynamodb_policy_doc = aws.iam.get_policy_document(
    statements=[
        {
            "effect": "Allow",
            "actions": [
                "dynamodb:BatchGetItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
            ],
            "resources": [visits_table.arn],
        }
    ]
)

dynamodb_policy = aws.iam.Policy(
    f"{lambda_name}-dynamodb-policy",
    name=f"{lambda_name}-dynamodb-policy",
    path="/",
    description="IAM policy for lambda to access DynamoDB",
    policy=dynamodb_policy_doc.json,
)

dynamodb_policy_attachment = aws.iam.RolePolicyAttachment(
    f"{lambda_name}-dynamodb-policy-attachment",
    role=lambda_role.name,
    policy_arn=dynamodb_policy.arn,
)

# Now create the lambda
lambda_archive = archive.get_file(
    type="zip",
    source_file="../api/main.py",
    output_path="api.zip",
)
lambda_function = aws.lambda_.Function(
    lambda_name,
    code=pulumi.FileArchive("api.zip"),
    name=lambda_name,
    role=lambda_role.arn,
    handler="main.handler",
    source_code_hash=lambda_archive.output_base64sha256,
    runtime=aws.lambda_.Runtime.PYTHON3D13,
    environment={"variables": {
        "TABLE_NAME": visits_table.name,
    }},
    logging_config={"log_format": "Text"},
    opts=pulumi.ResourceOptions(depends_on=[log_policy_attachment, log_group]),
)

# And make it accessible via HTTP
lambda_url = aws.lambda_.FunctionUrl(
    f"{lambda_name}-url",
    function_name=lambda_function.name,
    authorization_type="NONE",
    cors={
        "allow_origins": [],  # [f"https://{target_domain}"],
        "allow_methods": ["*"],
    }
)

## Static site

bucket = aws.s3.BucketV2("resume-bucket", bucket=target_domain)
bucket_name = bucket.id

website = aws.s3.BucketWebsiteConfigurationV2(
    "resume-website",
    bucket=bucket_name,
    index_document={"suffix": "index.html"},
    error_document={"key": "error.html"},
)

public_access_block = aws.s3.BucketPublicAccessBlock(
    "resume-public-access-block",
    bucket=bucket_name,
    block_public_acls=False,
)

public_read_policy = pulumi.Output.json_dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [
                    pulumi.Output.format("arn:aws:s3:::{0}/*", bucket_name),
                ],
            }
        ],
    }
)

bucket_policy = aws.s3.BucketPolicy(
    "bucket-policy",
    bucket=bucket_name,
    policy=public_read_policy,
    opts=pulumi.ResourceOptions(depends_on=[public_access_block]),
)

def upload_files(api_url):
    build_command = f"export LAMBDA_URL={api_url} && cd .. && pnpm install && pnpm build"
    print(f"Running build command: {build_command}")
    exit_status = os.system(build_command)
    if exit_status > 0:
        raise Exception("Build failed")

    files = os.listdir("../public")
    bucket_objects = []
    for file in files:
        mime_type, _ = mimetypes.guess_type(file)
        bucket_objects.append(
            aws.s3.BucketObject(
                file,
                bucket=bucket_name,
                source=pulumi.FileAsset(f"../public/{file}"),
                content_type=mime_type,
            )
        )

# Once the lambda is created, we can use its URL to build the app and upload it to the bucket
lambda_url.function_url.apply(upload_files)

pulumi.export("bucket_name", bucket_name)
pulumi.export("bucket_bucket", bucket.bucket)
pulumi.export("website_url", website.website_endpoint)
pulumi.export("website_domain", website.website_domain)
pulumi.export("lambda_name", lambda_function.name)
pulumi.export("lambda_url", lambda_url.function_url)
pulumi.export("visits_table_name", visits_table.name)
