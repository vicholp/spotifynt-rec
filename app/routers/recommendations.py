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
    temperature: float = 0.01

@router.post("/")
async def recommendation(request: NewRecommendationRequest):
    qdrant_service = QdrantService()
    qdrant_client = qdrant_service.get_client()

    all_points = qdrant_service.get_points(RECORDINGS_COLLECTION, request.track_ids)

    maest_avg   = np.mean([p.vector["maest"]   for p in all_points], axis=0)
    musicnn_avg = np.mean([p.vector["musicnn"] for p in all_points], axis=0)

    maest_last   = np.array(all_points[-1].vector["maest"])
    musicnn_last = np.array(all_points[-1].vector["musicnn"])

    query_maest   = (0.9 * maest_avg   + 0.1 * maest_last).tolist()
    query_musicnn = (0.9 * musicnn_avg + 0.1 * musicnn_last).tolist()

    results = qdrant_client.query_points(
        collection_name=RECORDINGS_COLLECTION,
        prefetch=[
            models.Prefetch(
                query=query_maest,
                using="maest",
                limit=200,
                score_threshold=0.85,
            ),
        ],
        query=query_musicnn,
        using="musicnn",
        query_filter=models.Filter(
            must_not=[
                models.HasIdCondition(has_id=request.track_ids)
            ]
        ),
        with_payload=True,
        limit=10,
    ).points

    results.sort(
        key=lambda r: r.payload.get("arousal", 0) + np.random.randn() * request.temperature * 8,
        reverse=True
    )

    return {"recommendations": [r.id for r in results]}
