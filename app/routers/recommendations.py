import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.minio_service import MinioService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService, RECORDINGS_COLLECTION
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from qdrant_client import models

router = APIRouter(
    prefix="/recommendations",
    responses={404: {"description": "Not found"}},
    tags=["recommendations"],
)

class NewRecommendationRequest(BaseModel):
    track_ids: list[int]

@router.post("/")
async def recommendation(request: NewRecommendationRequest):
    qdrant_service = QdrantService()
    qdrant_client = qdrant_service.get_client()

    last_three_tracks = request.track_ids[-3:]

    if len(last_three_tracks) == 1:
        weights = [1.0]
    elif len(last_three_tracks) == 2:
        weights = [0.35, 0.65]
    else:
        weights = [0.2, 0.3, 0.5]

    last_three_points = qdrant_service.get_points(RECORDINGS_COLLECTION, last_three_tracks)
    last_three_embeddings = [p.vector["discogs"] for p in last_three_points]

    vector = np.average(last_three_embeddings, axis=0, weights=weights)

    results = qdrant_client.query_points(
        collection_name=RECORDINGS_COLLECTION,
        query=vector.tolist(),
        using="discogs",
        query_filter=models.Filter(
            must_not=[
                models.HasIdCondition(has_id=request.track_ids)
            ]
        ),
        with_payload=True,
        limit=3
    ).points

    return {"recommendations": [r.id for r in results]}
