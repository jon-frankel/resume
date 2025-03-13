import mimetypes
import os

import pulumi_archive as archive
import pulumi_aws as aws

import pulumi

stack_config = pulumi.Config()
target_domain = stack_config.require("targetDomain")

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

files = os.listdir("../app/public")
bucketObjects = []
for file in files:
    mime_type, _ = mimetypes.guess_type(file)
    bucketObjects.append(
        aws.s3.BucketObject(
            file,
            bucket=bucket_name,
            source=pulumi.FileAsset(f"../app/public/{file}"),
            content_type=mime_type,
        )
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

# Set up permissions for lambda
lambda_name = "web-counter-lambda"
assume_role = aws.iam.get_policy_document(
    statements=[
        {
            "effect": "Allow",
            "principals": [{"identifiers": ["lambda.amazonaws.com"], "type": "Service"}],
            "actions": ["sts:AssumeRole"],
        }
    ]
)
iam_for_lambda = aws.iam.Role(
    f"{lambda_name}-role",
    name=f"{lambda_name}-role",
    assume_role_policy=assume_role.json,
)

# Give the lambda function permission to write logs
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
    role=iam_for_lambda.name,
    policy_arn=log_policy.arn,
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
    role=iam_for_lambda.arn,
    handler="main.handler",
    source_code_hash=lambda_archive.output_base64sha256,
    runtime=aws.lambda_.Runtime.PYTHON3D13,
    environment={"variables": {"BUCKET_NAME": bucket_name}},
    logging_config={"log_format": "Text"},
    opts=pulumi.ResourceOptions(depends_on=[log_policy_attachment, log_group]),
)

# And make it accessible via HTTP
lambda_url = aws.lambda_.FunctionUrl(
    f"{lambda_name}-url",
    function_name=lambda_function.name,
    authorization_type="NONE",
    cors={
        "allow_origins": ["*"],
        "allow_methods": ["*"],
    }
)

pulumi.export("bucket_name", bucket_name)
pulumi.export("bucket_bucket", bucket.bucket)
pulumi.export("website_url", website.website_endpoint)
pulumi.export("website_domain", website.website_domain)
pulumi.export("lambda_name", lambda_function.name)
pulumi.export("lambda_url", lambda_url.function_url)
