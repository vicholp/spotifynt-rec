import os
from minio import Minio
from minio.error import S3Error
from app.config import MINIO_ENDPOINT, MINIO_BUCKET, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
import tempfile


class MinioService:
    endpoint = MINIO_ENDPOINT
    bucket_name = MINIO_BUCKET
    access_key = MINIO_ACCESS_KEY
    secret_key = MINIO_SECRET_KEY

    def __init__(self):
        if not self.access_key or not self.secret_key:
            raise ValueError("Access key and secret key are required")

        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )

    def download_file(self, object_name: str) -> str:
        suffix = os.path.splitext(object_name)[1]
        if not suffix:
            suffix = ".tmp"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            try:
                self.client.fget_object(self.bucket_name, object_name, temp_file.name)
                return temp_file.name
            except S3Error as e:
                raise Exception(f"Failed to download file: {e}")
