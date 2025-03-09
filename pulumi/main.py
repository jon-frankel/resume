# import os
#
# import pulumi
# import pulumi_aws as aws
#
# dir_path = os.path.dirname(os.path.realpath(__file__))
#
# # Create an S3 Bucket
# bucket = aws.s3.Bucket(
#     "my-static-site-bucket",
#     website=aws.s3.BucketWebsiteArgs(
#         index_document="index.html",
#         error_document="error.html"
#     )
# )
#
# # Upload the HTML files
# index_html = aws.s3.BucketObject(
#     "index.html",
#     bucket=bucket.id,
#     source=pulumi.FileAsset("./index.html"),
#     acl="public-read"
# )
#
# error_html = aws.s3.BucketObject(
#     "error.html",
#     bucket=bucket.id,
#     source=pulumi.FileAsset("./error.html"),
#     acl="public-read"
# )
#
# # Create a Route 53 Hosted Zone
# hosted_zone = aws.route53.Zone("my-hosted-zone", name="example.com")
#
# # Create a Route 53 Record
# record = aws.route53.Record(
#     "my-record",
#     zone_id=hosted_zone.id,
#     name=hosted_zone.name,
#     type="A",
#     aliases=[aws.route53.RecordAliasArgs(
#         name=bucket.website_endpoint,
#         zone_id=bucket.hosted_zone_id,
#         evaluate_target_health=False
#     )]
# )
#
# # Export the bucket name and website URL
# pulumi.export("bucket_name", bucket.bucket)
# pulumi.export("website_url", bucket.website_endpoint)
# pulumi.export("hosted_zone_id", hosted_zone.id)
# pulumi.export("record_name", record.name)
