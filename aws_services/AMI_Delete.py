from aws_services import deregister_ami

ami_id_to_delete = "ami-06685995f570c8cdb"  
deregister_ami(ami_id_to_delete)
