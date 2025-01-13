from aws_services import create_ami_image
from aws_services import load_instances  # or from your state management module if separate

# Load stored instances (assuming a dictionary mapping server names to instance IDs)
instances = load_instances()

# Retrieve the instance ID for server1
server_id = instances.get("server1")

if server_id:
    # Provide a name for the AMI, e.g., "server1-backup"
    ami_name = "server1-backup"

    # Create an AMI from server1
    ami_id = create_ami_image(server_id, ami_name)

    if ami_id:
        print(f"Successfully created AMI: {ami_id} for server1.")
    else:
        print("Failed to create AMI for server1.")
else:
    print("Server1 instance ID not found.")
