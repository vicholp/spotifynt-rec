import logging
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.clients.minio_client import MinioService
from app.services.embedding_service import MainEmbeddingService, MaestEmbeddingService
from app.clients.qdrant_client import RECORDINGS_COLLECTION, QdrantService
from app.tasks import store_recording_task

router = APIRouter(
    prefix="/recordings",
    responses={404: {"description": "Not found"}},
    tags=["recordings"],
)

class CreateRecordingRequest(BaseModel):
    recording: dict
    file_url: Optional[str] = None
    queue: Optional[bool] = True

def get_payload_of_recording(recording: dict):
    tracks = recording.get('track', {})

    return {
        "id": recording['id'],
        "release_ids": [track.get('release_id') for track in tracks],
        "artist_ids": [track.get('release_id', {}).get('artist_id') for track in tracks],
    }


@router.post("/")
async def create(request: CreateRecordingRequest):
    if request.queue:
        task = store_recording_task.delay(request.recording, request.file_url)

        logging.info(f"Task {task.id} created for recording {request.recording['id']}")

        return {"task_id": task.id}

    minio_service = MinioService()
    main_service = MainEmbeddingService()
    maest_service = MaestEmbeddingService()
    qdrant_service = QdrantService()

    temp_file_path = minio_service.download_file(request.file_url)

    main_result = main_service.compute_audio_embeddings(temp_file_path)
    maest_result = maest_service.compute_maest_embedding(temp_file_path)
    vectors = {**main_result["vectors"], **maest_result["vectors"]}

    payload = get_payload_of_recording(request.recording)
    payload.update(main_result["features"])

    qdrant_service.insert_point(RECORDINGS_COLLECTION, request.recording['id'], vectors, payload)

    os.remove(temp_file_path)

    return {"message": "recording received"}

@router.get("/{recording_id}")
async def get_recording(recording_id: int):
    qdrant_service = QdrantService()
    collection_info = qdrant_service.get_collection_info(RECORDINGS_COLLECTION)

    if not collection_info:
        raise HTTPException(status_code=404, detail="Recording not found")

    point = qdrant_service.get_points(RECORDINGS_COLLECTION, [recording_id])

    if not point:
        raise HTTPException(status_code=404, detail="Recording not found")

    return {"recording": point[0].payload}
