import unittest
from unittest.mock import patch
from moto import mock_aws
import boto3
from aws_services import (
    create_ec2_instance,
    stop_instance,
    terminate_instance,
    create_ami_image,
    deregister_ami,
    create_s3_bucket,
    delete_s3_bucket,
    create_snapshot,
    delete_snapshot,
)

class TestAWSServices(unittest.TestCase):

    @mock_aws
    def test_create_ec2_instance(self):
        """Test creating an EC2 instance."""
        region_name = "eu-west-3"
        ec2 = boto3.client("ec2", region_name=region_name)

        # Create an instance
        instance_id = create_ec2_instance(
            "server1",
            "ami-12345678",
            "t2.micro",
            region_name=region_name
        )
        self.assertIsNotNone(instance_id)  # Ensure an instance ID is returned

        # Verify that an instance was created
        response = ec2.describe_instances()
        created_instances = [instance["InstanceId"] for r in response["Reservations"] for instance in r["Instances"]]
        self.assertIn(instance_id, created_instances)  # Check that the instance ID is in the list


    @mock_aws
    def test_terminate_instance(self):
        """Test terminating an EC2 instance."""
        region_name = "eu-west-3"
        ec2 = boto3.client("ec2", region_name=region_name)

        # Create a mock instance
        response = ec2.run_instances(
            ImageId="ami-12345678",
            InstanceType="t2.micro",
            MinCount=1,
            MaxCount=1,
        )
        instance_id = response["Instances"][0]["InstanceId"]

        # Terminate the instance
        terminate_instance(instance_id, region_name=region_name)

        response = ec2.describe_instances()
        # Ensure the instance is terminated
        instance_states = [i["State"]["Name"] for r in response["Reservations"] for i in r["Instances"]]
        self.assertIn("terminated", instance_states)

    @mock_aws
    def test_create_ami_image(self):
        """Test creating an AMI image."""
        region_name = "eu-west-3"
        ec2 = boto3.client("ec2", region_name=region_name)

        # Create a mock instance
        response = ec2.run_instances(
            ImageId="ami-12345678",
            InstanceType="t2.micro",
            MinCount=1,
            MaxCount=1,
        )
        instance_id = response["Instances"][0]["InstanceId"]

        # Create an AMI
        ami_id = create_ami_image(instance_id, "TestAMI", region_name=region_name)
        self.assertIsNotNone(ami_id)

    @mock_aws
    def test_deregister_ami(self):
        """Test deregistering an AMI."""
        region_name = "eu-west-3"
        ec2 = boto3.client("ec2", region_name=region_name)

        # Create a mock AMI
        response = ec2.run_instances(
            ImageId="ami-12345678",
            InstanceType="t2.micro",
            MinCount=1,
            MaxCount=1,
        )
        instance_id = response["Instances"][0]["InstanceId"]
        ami_response = ec2.create_image(InstanceId=instance_id, Name="TestAMI")
        ami_id = ami_response["ImageId"]

        # Deregister the AMI
        deregister_ami(ami_id, region_name=region_name)

        # Verify AMI is no longer in the list
        images = ec2.describe_images()["Images"]
        ami_ids = [image["ImageId"] for image in images]
        self.assertNotIn(ami_id, ami_ids)


    @mock_aws
    def test_create_and_delete_s3_bucket(self):
        """Test creating and deleting an S3 bucket."""
        region_name = "eu-west-3"
        bucket_name = "test-bucket"

        # Create bucket
        create_s3_bucket(bucket_name, region_name=region_name)
        s3 = boto3.client("s3", region_name=region_name)
        buckets = s3.list_buckets()["Buckets"]
        self.assertIn(bucket_name, [b["Name"] for b in buckets])

        # Delete bucket
        delete_s3_bucket(bucket_name, region_name=region_name)
        buckets = s3.list_buckets()["Buckets"]
        self.assertNotIn(bucket_name, [b["Name"] for b in buckets])

    @mock_aws
    def test_create_and_delete_snapshot(self):
        """Test creating and deleting an EBS snapshot."""
        region_name = "eu-west-3"
        ec2 = boto3.client("ec2", region_name=region_name)

        # Create a mock volume
        response = ec2.create_volume(Size=10, AvailabilityZone=f"{region_name}a")
        volume_id = response["VolumeId"]

        # Create snapshot
        snapshot_id = create_snapshot(volume_id, "Test snapshot", region_name=region_name)
        self.assertIsNotNone(snapshot_id)

        # Delete snapshot
        delete_snapshot(snapshot_id, region_name=region_name)

        # Verify snapshot deletion
        with self.assertRaises(Exception):
            ec2.describe_snapshots(SnapshotIds=[snapshot_id])

if __name__ == "__main__":
    unittest.main()
