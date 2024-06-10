from google.cloud import storage
import base64
import os
import base64


def upload_base64_image_to_gcs(image_base64, bucket_name, destination_blob_name):
    """Uploads a base64 encoded image to Google Cloud Storage

    Args:
        image_base64 (base64): Base64 encoded image
        bucket_name (str): The name of the bucket to upload to
        destination_blob_name (str): The name of the blob to be stored in GCS

    Returns:
        str: URI of the uploaded image
    """
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        image_data = base64.b64decode(image_base64)
        blob.upload_from_string(image_data)
        return f"gs://{bucket_name}/{destination_blob_name}"
    except Exception as e:
        return(f"ERROR: {e}")

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from a bucket

    Args:
        bucket_name (str): The name of the bucket to delete from
        blob_name (str): The name of the blob to delete
    """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    