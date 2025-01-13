from aws_services import create_snapshot

volume_id = "vol-07f7fb2cc7a93775c"  # Replace with your actual volume ID
description = "Snapshot of server1 volume"
snapshot_id = create_snapshot(volume_id, description)

if snapshot_id:
    print(f"Successfully created snapshot: {snapshot_id}")
else:
    print("Snapshot creation failed.")
