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

    vectors = embedding_service.compute_audio_embeddings(temp_file_path)

    payload = get_payload_of_recording(request.recording)

    qdrant_service.insert_point(RECORDINGS_COLLECTION, request.recording['id'], vectors, payload)

    return {"message": "recording received"}

