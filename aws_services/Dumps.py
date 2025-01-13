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
    try:
        # Load existing server-instance mappings
        instances = load_instances()
        # Check if the server_name already exists
        if server_name in instances:
            existing_id = instances[server_name]
            print(f"{server_name} already exists with ID: {existing_id}. Not creating a new one.")
            return existing_id

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

        # Store the new instance under the given server_name
        instances[server_name] = instance_id
        save_instances(instances)

        return instance_id
    except Exception as e:
        print(f"Error creating EC2 instance: {e}")
        return None