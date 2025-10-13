"""
Google Cloud Storage utilities for call processing.

This module provides functions for uploading, downloading, and listing files
in Google Cloud Storage buckets used by the call processing pipeline.
"""

from google.cloud import storage
from django.conf import settings


def upload_to_gcs(file_obj, destination_blob_name):
    """
    Upload a file-like object to Google Cloud Storage.

    Args:
        file_obj: File-like object to upload
        destination_blob_name (str): Target blob name in the bucket

    Returns:
        str: Full GCS URI of the uploaded file
    """
    client = storage.Client()
    bucket = client.bucket(f"{settings.GOOGLE_CLOUD_PROJECT}_{settings.CALL_PROCESSING_BUCKET}")
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file_obj, rewind=True)
    return f"gs://{settings.GOOGLE_CLOUD_PROJECT}_{settings.CALL_PROCESSING_BUCKET}/{destination_blob_name}"


def download_from_gcs(destination_blob_name):
    """
    Download a file from Google Cloud Storage and return its contents.

    Args:
        destination_blob_name (str): Name of the blob to download

    Returns:
        bytes: File contents as bytes
    """
    client = storage.Client()
    bucket = client.bucket(f"{settings.GOOGLE_CLOUD_PROJECT}_{settings.CALL_PROCESSING_BUCKET}")
    blob = bucket.blob(destination_blob_name)
    return blob.download_as_bytes()


def list_files_in_gcs(directory_path: str, match_glob: str = None):
    """
    List blobs in GCS with the specified directory path and optional glob pattern.

    Args:
        directory_path (str): Directory prefix to filter blobs
        match_glob (str, optional): Glob pattern to match blob names

    Returns:
        list[str]: List of blob names matching the criteria
    """
    client = storage.Client()
    bucket = client.bucket(f"{settings.GOOGLE_CLOUD_PROJECT}_{settings.CALL_PROCESSING_BUCKET}")
    blobs = bucket.list_blobs(prefix=directory_path, match_glob=match_glob)
    return [blob.name for blob in blobs]
