import json
import boto3
from typing import Optional, List

def create_ec2_instance(
    ami_id: str,
    instance_type: str,
    *,
    region_name: str = "us-east-1",
    user_data: Optional[str] = None,
    key_name: Optional[str] = None,
    security_group_ids: Optional[List[str]] = None,
    subnet_id: Optional[str] = None,
    tag_specifications: Optional[List[dict]] = None,
) -> Optional[str]:
    try:
        ec2 = boto3.client("ec2", region_name=region_name)
        if not ami_id:
            raise ValueError("AMI ID (ami_id) is mandatory.")
        if not instance_type:
            raise ValueError("Instance type (instance_type) is mandatory.")
        params = {
            "ImageId": ami_id,
            "InstanceType": instance_type,
            "MinCount": 1,
            "MaxCount": 1,
        }
        if user_data:
            params["UserData"] = user_data
        if key_name:
            params["KeyName"] = key_name
        if security_group_ids:
            params["SecurityGroupIds"] = security_group_ids
        if subnet_id:
            params["SubnetId"] = subnet_id
        if tag_specifications:
            params["TagSpecifications"] = tag_specifications

        response = ec2.run_instances(**params)
        instance_id = response["Instances"][0]["InstanceId"]
        print(f"EC2 instance created with ID: {instance_id}")
        return instance_id
    except Exception as e:
        print(f"Error creating EC2 instance: {e}")
        return None

def stop_instance(instance_id: str, region_name: str = "us-east-1") -> None:
    try:
        if not instance_id:
            raise ValueError("Instance ID is required to stop an instance.")
        ec2 = boto3.client("ec2", region_name=region_name)
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"EC2 instance {instance_id} stopping...")
    except Exception as e:
        print(f"Error stopping instance {instance_id}: {e}")

def terminate_instance(instance_id: str, region_name: str = "us-east-1") -> None:
    try:
        if not instance_id:
            raise ValueError("Instance ID is required to terminate an instance.")
        ec2 = boto3.client("ec2", region_name=region_name)
        ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"EC2 instance {instance_id} terminated...")
    except Exception as e:
        print(f"Error terminating instance {instance_id}: {e}")

def create_ami_image(instance_id: str, name: str, region_name: str = "us-east-1") -> Optional[str]:
    try:
        ec2 = boto3.client("ec2", region_name=region_name)
        response = ec2.create_image(InstanceId=instance_id, Name=name, NoReboot=True)
        image_id = response["ImageId"]
        print(f"AMI image created with ID: {image_id}")
        return image_id
    except Exception as e:
        print(f"Error creating AMI image from instance {instance_id}: {e}")
        return None

def create_s3_bucket(bucket_name: str, region_name: str = "us-east-1") -> None:
    try:
        s3 = boto3.client("s3", region_name=region_name)
        if region_name == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            location = {'LocationConstraint': region_name}
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print(f"S3 bucket '{bucket_name}' created in region {region_name}.")
    except Exception as e:
        print(f"Error creating S3 bucket {bucket_name}: {e}")

def create_lambda_function(function_name: str, role_arn: str, handler: str, 
                           zip_file_path: str, runtime: str = "python3.8", 
                           region_name: str = "us-east-1") -> Optional[str]:
    try:
        lambda_client = boto3.client("lambda", region_name=region_name)
        with open(zip_file_path, 'rb') as f:
            zipped_code = f.read()

        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': zipped_code},
            Publish=True
        )
        function_arn = response["FunctionArn"]
        print(f"Lambda function '{function_name}' created with ARN: {function_arn}")
        return function_arn
    except Exception as e:
        print(f"Error creating Lambda function {function_name}: {e}")
        return None

def create_iam_role(role_name: str, assume_role_policy_document: dict, region_name: str = "us-east-1") -> Optional[str]:
    try:
        iam = boto3.client("iam")
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
        )
        role_arn = response["Role"]["Arn"]
        print(f"IAM role '{role_name}' created with ARN: {role_arn}")
        return role_arn
    except Exception as e:
        print(f"Error creating IAM role {role_name}: {e}")
        return None

def attach_policy_to_role(role_name: str, policy_arn: str, region_name: str = "us-east-1") -> None:
    try:
        iam = boto3.client("iam")
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print(f"Policy {policy_arn} attached to role {role_name}.")
    except Exception as e:
        print(f"Error attaching policy {policy_arn} to role {role_name}: {e}")
