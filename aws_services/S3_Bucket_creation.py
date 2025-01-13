from aws_services import create_s3_bucket

bucket_name = "abhinav-bijpuria-s3-bucket"
create_s3_bucket(bucket_name, region_name="eu-west-3")