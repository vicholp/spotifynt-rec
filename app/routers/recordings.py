import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.minio_service import MinioService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import RECORDINGS_COLLECTION, QdrantService

router = APIRouter(
    prefix="/recordings",
    responses={404: {"description": "Not found"}},
    tags=["recordings"],
)

class CreateRecordingRequest(BaseModel):
    recording: dict
    file_url: Optional[str] = None

def get_payload_of_recording(recording: dict):
    tracks = recording.get('track', {})

    return {
        "id": recording['id'],
        "release_ids": [track.get('release_id') for track in tracks],
        "artist_ids": [track.get('release_id', {}).get('artist_id') for track in tracks],
    }


@router.post("/")
async def create(request: CreateRecordingRequest):
    minio_service = MinioService()
    embedding_service = EmbeddingService()
    qdrant_service = QdrantService()

    temp_file_path = minio_service.download_file(request.file_url)

    result = embedding_service.compute_audio_embeddings(temp_file_path)

    payload = get_payload_of_recording(request.recording)
    payload.update(result["features"])

    qdrant_service.insert_point(RECORDINGS_COLLECTION, request.recording['id'], result["vectors"], payload)

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
