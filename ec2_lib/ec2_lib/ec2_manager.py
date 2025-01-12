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
) -> str:
    # ... [existing create_ec2_instance code] ...
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

def stop_instance(instance_id: str, region_name: str = "us-east-1") -> None:
    """
    Stops the specified EC2 instance.
    """
    if not instance_id:
        raise ValueError("Instance ID is required to stop an instance.")
    ec2 = boto3.client("ec2", region_name=region_name)
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"EC2 instance {instance_id} stopping...")

def terminate_instance(instance_id: str, region_name: str = "us-east-1") -> None:
    """
    Terminates the specified EC2 instance.
    """
    if not instance_id:
        raise ValueError("Instance ID is required to terminate an instance.")
    ec2 = boto3.client("ec2", region_name=region_name)
    ec2.terminate_instances(InstanceIds=[instance_id])
    print(f"EC2 instance {instance_id} terminated.")
