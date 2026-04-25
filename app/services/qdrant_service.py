import os
from typing import Optional
from minio import Minio
from minio.error import S3Error
import uuid
# from app.config import MINIO_ENDPOINT, MINIO_BUCKET, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
from app.config import QDRANT_HOST
import tempfile


from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client import QdrantClient, models
import glob

import os
import glob
import numpy as np
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs
from sklearn.metrics.pairwise import cosine_similarity
import json
from qdrant_client.models import PointStruct

RECORDINGS_COLLECTION = "recordings_collection"
RELEASES_COLLECTION = "releases_collection"
ARTISTS_COLLECTION = "artists_collection"

class QdrantService:
    endpoint = QDRANT_HOST

    def __init__(self):
        self.client = QdrantClient(self.endpoint) # Connect to existing Qdrant instance

    def create_collections(self):
        self.client.create_collection(
            collection_name="recordings_collection",
            vectors_config={
                "discogs": models.VectorParams(size=1280, distance=models.Distance.COSINE),
                "musicnn": models.VectorParams(size=200, distance=models.Distance.COSINE),
                "maest": models.VectorParams(size=2304, distance=models.Distance.COSINE),
                "mood": models.VectorParams(size=5, distance=models.Distance.COSINE),
                "arousal_valence": models.VectorParams(size=2, distance=models.Distance.COSINE),
                "lyrics": models.VectorParams(size=1024, distance=models.Distance.COSINE),
            },
            sparse_vectors_config={
                "lyrics_sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            }
        )

        self.client.create_collection(
            collection_name="releases_collection",
            vectors_config={
                "discogs": models.VectorParams(size=1280, distance=models.Distance.COSINE),
                "musicnn": models.VectorParams(size=200, distance=models.Distance.COSINE),
                "maest": models.VectorParams(size=2304, distance=models.Distance.COSINE),
                "mood": models.VectorParams(size=5, distance=models.Distance.COSINE),
                "arousal_valence": models.VectorParams(size=2, distance=models.Distance.COSINE),
                "lyrics": models.VectorParams(size=1024, distance=models.Distance.COSINE),
            },
            sparse_vectors_config={
                "lyrics_sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            }
        )

        self.client.create_collection(
            collection_name="artists_collection",
            vectors_config={
                "discogs": models.VectorParams(size=1280, distance=models.Distance.COSINE),
                "musicnn": models.VectorParams(size=200, distance=models.Distance.COSINE),
                "maest": models.VectorParams(size=2304, distance=models.Distance.COSINE),
                "mood": models.VectorParams(size=5, distance=models.Distance.COSINE),
                "arousal_valence": models.VectorParams(size=2, distance=models.Distance.COSINE),
                "lyrics": models.VectorParams(size=1024, distance=models.Distance.COSINE),
            },
            sparse_vectors_config={
                "lyrics_sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            }
        )


    def get_client(self):
        return self.client

    def get_collection_info(self, collection_name: str):
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        self.client.delete_collection(collection_name=collection_name)


    def insert_point(self, collection_name: str, point_id: str, vector: dict, payload: dict):
        self.client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def get_points(self, collection_name: str, point_ids: list[str]):
        return self.client.retrieve(
            collection_name=collection_name,
            ids=point_ids,
            with_vectors=True,
            with_payload=True
        )


