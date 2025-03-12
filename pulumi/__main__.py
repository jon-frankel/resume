import mimetypes
import os

import pulumi
from pulumi_aws import s3

stack_config = pulumi.Config()
target_domain = stack_config.require("targetDomain")

bucket = s3.BucketV2("resume-bucket", bucket=target_domain)
bucket_name = bucket.id

website = s3.BucketWebsiteConfigurationV2(
    "resume-website",
    bucket=bucket_name,
    index_document={"suffix": "index.html"},
    error_document={"key": "error.html"},
)

public_access_block = s3.BucketPublicAccessBlock(
    "resume-public-access-block",
    bucket=bucket_name,
    block_public_acls=False,
)

files = os.listdir("../app/public")
bucketObjects = []
for file in files:
    mime_type, _ = mimetypes.guess_type(file)
    bucketObjects.append(
        s3.BucketObject(
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

bucket_policy = s3.BucketPolicy(
    "bucket-policy",
    bucket=bucket_name,
    policy=public_read_policy,
    opts=pulumi.ResourceOptions(depends_on=[public_access_block]),
)

pulumi.export("bucket_name", bucket_name)
pulumi.export("bucket_bucket", bucket.bucket)
pulumi.export("website_url", website.website_endpoint)
