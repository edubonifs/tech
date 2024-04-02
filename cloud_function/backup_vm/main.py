import google.auth
from google.cloud.devtools.cloudbuild_v1.types import Build
from google.cloud.devtools.cloudbuild_v1 import CloudBuildClient
from google.cloud import compute_v1
from google.cloud import storage
import datetime
import time

def backup_vm(request):
    project_id = "carbon-nucleus-211209"
    vm_name = "my-mongo"
    zone = "us-central1-a"
    bucket_name = "mongo-bucket-test"
    disk_name = "instance-20240325-093211"

    compute_client = compute_v1.DisksClient()
    images_client = compute_v1.ImagesClient()
    storage_client = storage.Client()

    # Generate names for the snapshot and image
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    snapshot_name = f"snapshot-{vm_name}-{timestamp}"
    image_name = f"vm-backup-{vm_name}-{timestamp}"

    # Create a snapshot of the disk
    snapshot_body = compute_v1.Snapshot(name=snapshot_name)
    operation = compute_client.create_snapshot(project=project_id, zone=zone, disk=disk_name, snapshot_resource=snapshot_body)
    wait_for_operation(project_id=project_id, operation_id=operation.name, zone=zone)

    # Create an image from the snapshot
    image_body = compute_v1.Image(name=image_name, source_snapshot=f"projects/{project_id}/global/snapshots/{snapshot_name}")
    operation = images_client.insert(project=project_id, image_resource=image_body)
    # Corrected call for global operation (without zone)
    wait_for_operation(project_id=project_id, operation_id=operation.name)

    export_image_to_bucket(project_id, image_name, bucket_name)

    return f"Backup process initiated for {vm_name}, snapshot: {snapshot_name}, image: {image_name}, export to {bucket_name} started."

    # TODO: Export the image to Cloud Storage if needed

    return f"Backup process initiated for {vm_name}, snapshot: {snapshot_name}, image: {image_name}"

def wait_for_operation(project_id, operation_id, zone=None):
    """Waits for the specified operation (zonal or global) to complete."""
    if zone:
        # Handle zonal operation
        service = compute_v1.ZoneOperationsClient()
        print(f"Waiting for zonal operation {operation_id} in {zone} to complete...")
        while True:
            op = service.get(project=project_id, zone=zone, operation=operation_id)
            if op.status == compute_v1.Operation.Status.DONE:
                print("Zonal operation completed.")
                if op.error:
                    errors = ', '.join(e.message for e in op.error.errors)
                    raise Exception(f"Operation resulted in errors: {errors}")
                break
    else:
        # Handle global operation
        service = compute_v1.GlobalOperationsClient()
        print(f"Waiting for global operation {operation_id} to complete...")
        while True:
            op = service.get(project=project_id, operation=operation_id)
            if op.status == compute_v1.Operation.Status.DONE:
                print("Global operation completed.")
                if op.error:
                    errors = ', '.join(e.message for e in op.error.errors)
                    raise Exception(f"Operation resulted in errors: {errors}")
                break
    time.sleep(2)

def export_image_to_bucket(project_id, image_name, destination_bucket):
    client = CloudBuildClient()
    # Correctly construct the build request using the Build class
    build = Build()
    build.steps = [{
        'name': 'gcr.io/cloud-builders/gcloud',
        'args': [
            'compute', 'images', 'export',
            '--destination-uri', f'gs://{destination_bucket}/{image_name}.tar.gz',
            '--image', image_name,
            '--project', project_id
        ]
    }]
    # Trigger the build
    operation = client.create_build(project_id=project_id, build=build)
    print(f"Triggered image export to bucket: gs://{destination_bucket}/{image_name}.tar.gz")

