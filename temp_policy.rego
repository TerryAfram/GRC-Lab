package main

deny[msg] {
    r := input.resources[_]
    r.type == "aws_s3_bucket"
    r.values.acl == "public-read"
    msg = "S3 bucket is publicly accessible"
}