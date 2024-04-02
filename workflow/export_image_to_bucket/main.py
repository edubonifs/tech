from google.cloud.devtools.cloudbuild_v1.types import Build
from google.cloud.devtools.cloudbuild_v1 import CloudBuildClient

def export_image_to_bucket(request):
    request_json = request.get_json(silent=True)
    project_id = request_json['project_id']
    image_name = request_json['image_name']
    bucket_name = request_json['bucket_name']

    client = CloudBuildClient()

    build = Build()
    build.steps = [{
        'name': 'gcr.io/cloud-builders/gcloud',
        'args': [
            'compute', 'images', 'export',
            '--destination-uri', f'gs://{bucket_name}/{image_name}.tar.gz',
            '--image', image_name,
            '--project', project_id
        ]
    }]

    client.create_build(project_id=project_id, build=build)

    return f"Image export to bucket initiated: {image_name}."
