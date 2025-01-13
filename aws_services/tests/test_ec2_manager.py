# tests/test_ec2_manager.py

import pytest
from ec2_lib import create_ec2_instance

def test_create_ec2_instance(mocker):
    # Mock the boto3 client
    mock_ec2_client = mocker.patch("boto3.client")
    mock_run_instances = mock_ec2_client.return_value.run_instances
    mock_run_instances.return_value = {
        "Instances": [{"InstanceId": "i-1234567890abcdef"}]
    }

    instance_id = create_ec2_instance(
        ami_id="ami-12345",
        instance_type="t2.micro",
        key_name="my-key",
        security_group_ids=["sg-12345"],
        subnet_id="subnet-67890"
    )

    assert instance_id == "i-1234567890abcdef"
    mock_run_instances.assert_called_once()
