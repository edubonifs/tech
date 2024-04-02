from google.cloud import compute_v1
import datetime
import time

def wait_for_operation(project_id, operation_id, zone=None):
    """Waits for the specified operation (zonal or global) to complete."""
    if zone:
        service = compute_v1.ZoneOperationsClient()
    else:
        service = compute_v1.GlobalOperationsClient()

    print(f"Waiting for operation {operation_id} to complete...")
    while True:
        if zone:
            op = service.get(project=project_id, zone=zone, operation=operation_id)
        else:
            op = service.get(project=project_id, operation=operation_id)

        if op.status == compute_v1.Operation.Status.DONE:
            print("Operation completed.")
            if op.error:
                errors = ', '.join(e.message for e in op.error.errors)
                raise Exception(f"Operation resulted in errors: {errors}")
            break
        time.sleep(2)

def create_snapshot_and_image(request):
    request_json = request.get_json(silent=True)
    project_id = request_json['project_id']
    vm_name = request_json['vm_name']
    zone = request_json['zone']
    disk_name = request_json['disk_name']

    compute_client = compute_v1.DisksClient()
    images_client = compute_v1.ImagesClient()

    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    snapshot_name = f"snapshot-{vm_name}-{timestamp}"
    image_name = f"vm-backup-{vm_name}-{timestamp}"

    # Create a snapshot of the disk
    operation = compute_client.create_snapshot(project=project_id, zone=zone, disk=disk_name, snapshot_resource=compute_v1.Snapshot(name=snapshot_name))
    wait_for_operation(project_id, operation.name, zone)

    # Create an image from the snapshot
    operation = images_client.insert(project=project_id, image_resource=compute_v1.Image(name=image_name, source_snapshot=f"projects/{project_id}/global/snapshots/{snapshot_name}"))
    wait_for_operation(project_id, operation.name)

    return {
        'image_name': image_name,
        'message': f"Snapshot and image creation initiated for {vm_name}."
    }

