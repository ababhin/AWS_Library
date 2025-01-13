from aws_services import create_ec2_instance

server1_id = create_ec2_instance("server1", "ami-049a0782ca02dc58c", "t2.micro")
# server2_id = create_ec2_instance("server2", "ami-049a0782ca02dc58c", "t2.micro")
# server3_id = create_ec2_instance("server3", "ami-049a0782ca02dc58c", "t2.micro")

