import os
import json
import boto3
from typing import Optional, List

# Use environment variable for default region, fallback to 'eu-west-3' if not set.
DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'eu-west-3')

# File to store active instance information (mapping server names to IDs)
INSTANCES_FILE = "instances.json"

def load_instances() -> dict:
    """Load server-instance mappings from the JSON file."""
    if os.path.exists(INSTANCES_FILE):
        try:
            with open(INSTANCES_FILE, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}

def save_instances(instances: dict) -> None:
    """Save server-instance mappings to the JSON file."""
    with open(INSTANCES_FILE, 'w') as f:
        json.dump(instances, f)

def create_ec2_instance(
    server_name: str,
    ami_id: str,
    instance_type: str,
    *,
    region_name: str = DEFAULT_REGION,
    user_data: Optional[str] = None,
    key_name: Optional[str] = None,
    security_group_ids: Optional[List[str]] = None,
    subnet_id: Optional[str] = None,
    tag_specifications: Optional[List[dict]] = None,
) -> Optional[str]:
    """
    Creates an EC2 instance with the given configuration.
    """
    try:
        ec2 = boto3.client("ec2", region_name=region_name)
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


def stop_instance(instance_id: str, region_name: str = DEFAULT_REGION) -> None:
    try:
        if not instance_id:
            raise ValueError("Instance ID is required to stop an instance.")
        ec2 = boto3.client("ec2", region_name=region_name)
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"EC2 instance {instance_id} stopping...")
    except Exception as e:
        print(f"Error stopping instance {instance_id}: {e}")

def terminate_instance(instance_id, region_name: str = DEFAULT_REGION) -> None:
    """
    Terminates one or more EC2 instances and removes them from the JSON store.
    Accepts a single instance ID (str), a list of instance IDs, or a comma-separated string of IDs.
    """
    try:
        if not instance_id:
            raise ValueError("Instance ID is required to terminate an instance.")
        
        # Determine the list of instance IDs from input
        if isinstance(instance_id, str):
            # Check if the string contains commas to split multiple IDs
            if ',' in instance_id:
                instance_ids = [id_.strip() for id_ in instance_id.split(',') if id_.strip()]
            else:
                instance_ids = [instance_id]
        elif isinstance(instance_id, list):
            instance_ids = instance_id
        else:
            raise ValueError("Instance ID must be a string or a list of strings.")

        ec2 = boto3.client("ec2", region_name=region_name)
        ec2.terminate_instances(InstanceIds=instance_ids)
        print(f"EC2 instance(s) {', '.join(instance_ids)} terminated...")

        # Remove terminated instance IDs from the JSON store
        instances = load_instances()
        # Remove any instance IDs that match the terminated ones
        for key, val in list(instances.items()):
            if val in instance_ids:
                del instances[key]
        save_instances(instances)

    except Exception as e:
        print(f"Error terminating instance(s) {instance_id}: {e}")

def create_ami_image(instance_id: str, name: str, region_name: str = DEFAULT_REGION) -> Optional[str]:
    try:
        ec2 = boto3.client("ec2", region_name=region_name)
        response = ec2.create_image(InstanceId=instance_id, Name=name, NoReboot=True)
        image_id = response["ImageId"]
        print(f"AMI image created with ID: {image_id}")
        return image_id
    except Exception as e:
        print(f"Error creating AMI image from instance {instance_id}: {e}")
        return None

def deregister_ami(image_id: str, region_name: str = DEFAULT_REGION) -> None:
    """
    Deregisters (deletes) an AMI image.
    """
    try:
        ec2 = boto3.client("ec2", region_name=region_name)
        ec2.deregister_image(ImageId=image_id)
        print(f"Deregistered AMI: {image_id}")
    except Exception as e:
        print(f"Error deregistering AMI {image_id}: {e}")


def create_s3_bucket(bucket_name: str, region_name: str = DEFAULT_REGION) -> None:
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

def delete_s3_bucket(bucket_name: str, region_name: str = DEFAULT_REGION) -> None:
    """
    Deletes all objects in the specified S3 bucket and then deletes the bucket.
    """
    try:
        s3 = boto3.client("s3", region_name=region_name)

        # Delete all objects and versions in the bucket
        paginator = s3.get_paginator('list_object_versions')
        for page in paginator.paginate(Bucket=bucket_name):
            versions = page.get('Versions', []) + page.get('DeleteMarkers', [])
            for version in versions:
                s3.delete_object(
                    Bucket=bucket_name,
                    Key=version['Key'],
                    VersionId=version['VersionId']
                )
        # After emptying, delete the bucket
        s3.delete_bucket(Bucket=bucket_name)
        print(f"S3 bucket '{bucket_name}' deleted in region {region_name}.")
    except Exception as e:
        print(f"Error deleting S3 bucket {bucket_name}: {e}")

def create_snapshot(volume_id: str, description: str, region_name: str = DEFAULT_REGION) -> Optional[str]:
    """
    Creates an EBS snapshot for the specified volume and returns its snapshot ID.
    """
    try:
        ec2 = boto3.client("ec2", region_name=region_name)
        response = ec2.create_snapshot(VolumeId=volume_id, Description=description)
        snapshot_id = response["SnapshotId"]
        print(f"Snapshot created with ID: {snapshot_id}")
        return snapshot_id
    except Exception as e:
        print(f"Error creating snapshot for volume {volume_id}: {e}")
        return None

def delete_snapshot(snapshot_id: str, region_name: str = DEFAULT_REGION) -> None:
    """
    Deletes the specified EBS snapshot.
    """
    try:
        ec2 = boto3.client("ec2", region_name=region_name)
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        print(f"Snapshot {snapshot_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting snapshot {snapshot_id}: {e}")


def create_lambda_function(function_name: str, role_arn: str, handler: str, 
                           zip_file_path: str, runtime: str = "python3.8", 
                           region_name: str = DEFAULT_REGION) -> Optional[str]:
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

