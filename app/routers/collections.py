from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.minio_service import MinioService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

router = APIRouter(
    prefix="/collections",
    responses={404: {"description": "Not found"}},
    tags=["collections"],
)

@router.post("/")
def create_collections():
    qdrant_service = QdrantService()
    qdrant_service.create_collections()

    return {"message": "Collection created"}

@router.delete("/")
def delete_collection(collection_name: str):
    qdrant_service = QdrantService()
    qdrant_service.delete_collection(collection_name=collection_name)

    return {"message": "Collection deleted"}

@router.get("/")
def get_collection_info(collection_name: str):
    qdrant_service = QdrantService()
    info = qdrant_service.get_collection_info(collection_name=collection_name)

    return {"collection_info": info.dict()}

