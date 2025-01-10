from google.cloud import storage
from django.conf import settings


def upload_to_gcs(file_obj, destination_blob_name):
    """Upload a file-like object to GCS."""
    client = storage.Client()
    bucket = client.bucket(f"{settings.GOOGLE_CLOUD_PROJECT}_{settings.CALL_PROCESSING_BUCKET}")
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file_obj, rewind=True)
    return f"gs://{settings.GOOGLE_CLOUD_PROJECT}_{settings.CALL_PROCESSING_BUCKET}/{destination_blob_name}"


def download_from_gcs(destination_blob_name):
    """Download a file from GCS and return its contents."""
    client = storage.Client()
    bucket = client.bucket(settings.CALL_PROCESSING_BUCKET)
    blob = bucket.blob(destination_blob_name)
    return blob.download_as_bytes()
