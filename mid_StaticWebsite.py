#!/usr/bin/env python
import mimetypes
import os
import json

from constructs import Construct
from cdktf import App, NamedRemoteWorkspace, TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket, S3BucketConfig, S3BucketWebsite
from cdktf_cdktf_provider_aws.s3_bucket_website_configuration import S3BucketWebsiteConfiguration
from cdktf_cdktf_provider_aws.s3_bucket_acl import S3BucketAcl
from cdktf_cdktf_provider_aws.s3_bucket_ownership_controls import S3BucketOwnershipControls, S3BucketOwnershipControlsRule
from cdktf_cdktf_provider_aws.s3_bucket_public_access_block import S3BucketPublicAccessBlock
from cdktf_cdktf_provider_aws.s3_bucket_policy import S3BucketPolicy
from cdktf_cdktf_provider_aws.s3_object import S3Object




class StaticWebsiteStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS", region="us-east-1")

        bucket = S3Bucket(self, "MyBucket",
                          bucket="tf-eg-static-mid1"
                          )
        
        website_config = S3BucketWebsiteConfiguration(self, "WebsiteConfiguration",
                            bucket=bucket.bucket,
                            index_document={ "suffix":"index.html"},
                            error_document={ "key":"error.html"}
                            )
        
        TerraformOutput(self, "website_url",
                value=website_config.website_endpoint,
                )
        
        
        bucket_ownership_controls = S3BucketOwnershipControls(self, "BucketOwnershipControls",
                                    bucket=bucket.bucket,
                                    rule=S3BucketOwnershipControlsRule(object_ownership="BucketOwnerPreferred")
                                    )
        bucket_public_access_block = S3BucketPublicAccessBlock(self, "BucketPublicAccessBlock", 
                                    bucket=bucket.bucket,
                                    block_public_acls=False,
                                    block_public_policy=False,
                                    ignore_public_acls=False,
                                    restrict_public_buckets=False)
        
        bucket_acl = S3BucketAcl(self, "MyBucketAcl", bucket=bucket.bucket, acl="public-read", depends_on = [bucket_ownership_controls, bucket_public_access_block])
        
        
        bucket_policy = S3BucketPolicy(self, "PublicReadPolicy", 
                        bucket=bucket.bucket, 
                         policy=json.dumps({
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Sid": "PublicReadGetObject",
                                    "Effect": "Allow",
                                    "Principal": "*",
                                    "Action": "s3:GetObject",
                                    "Resource": "arn:aws:s3:::"+bucket.bucket+"/*"
                                }
                            ]
                        }),
                        depends_on = [bucket_acl] )
        
        
        location="/home/ec2-user/environment/Terraform/static_website"
        
        for root, dirs, files in os.walk(location):

            for file in files:
                print(os.path.join(root, file))
                file_rel_path = os.path.join(root, file)
                mime_type, _ = mimetypes.guess_type(file_rel_path)
                file_location_s3 = os.path.sep.join(file_rel_path.split(os.path.sep)[1:])
                print(file_rel_path, " ", file_location_s3 , " ", mime_type )
                S3Object(self, "object-"+file_location_s3, 
                            bucket=bucket.bucket, 
                            key=file_location_s3, 
                            source=os.path.abspath(file_rel_path), 
                            content_type=mime_type )
        
        
    
app = App()
StaticWebsiteStack(app, "static_website")

app.synth()