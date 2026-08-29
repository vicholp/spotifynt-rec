import os
from celery import Celery
from app.clients.minio_client import MinioService
from app.services.embedding_service import MainEmbeddingService, MaestEmbeddingService
from app.clients.qdrant_client import RECORDINGS_COLLECTION, QdrantService
from app.config import CELERY_BROKER_URL
import logging

app = Celery("tasks", broker=CELERY_BROKER_URL)


@app.task
def store_recording_task(recording: dict, file_url: str):
    compute_main_embeddings_task.delay(recording, file_url)
    compute_maest_embedding_task.delay(recording["id"], file_url)


@app.task(queue='main')
def compute_main_embeddings_task(recording: dict, file_url: str):
    minio_service = MinioService()
    temp_file_path = minio_service.download_file(file_url)
    try:
        result = MainEmbeddingService().compute_audio_embeddings(temp_file_path)
    finally:
        os.remove(temp_file_path)

    payload = {
        "id": recording["id"],
        "release_ids": [track.get("release_id") for track in recording.get("track", [])],
        "artist_ids": [track.get("release_id", {}).get("artist_id") for track in recording.get("track", [])],
    }
    payload.update(result["features"])

    try:
        QdrantService().insert_point(RECORDINGS_COLLECTION, recording["id"], result["vectors"], payload)
        logging.info(f"Stored main embeddings for recording {recording.get('id')}")
    except Exception as e:
        logging.error(f"Failed to store main embeddings for recording {recording.get('id')}: {str(e)}")
        raise


@app.task(queue='maest', bind=True, max_retries=5, default_retry_delay=10)
def compute_maest_embedding_task(self, recording_id: str, file_url: str):
    minio_service = MinioService()
    temp_file_path = minio_service.download_file(file_url)
    try:
        result = MaestEmbeddingService().compute_maest_embedding(temp_file_path)
    finally:
        os.remove(temp_file_path)

    try:
        QdrantService().update_vectors(RECORDINGS_COLLECTION, recording_id, result["vectors"])
        logging.info(f"Stored maest embedding for recording {recording_id}")
    except Exception as e:
        logging.warning(f"update_vectors failed for recording {recording_id}, retrying: {str(e)}")
        raise self.retry(exc=e)
