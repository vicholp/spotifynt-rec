import json
import app.clients.redis_client as redis_client
from app.config import REDIS_HOST, REDIS_PORT
from typing import Optional

THREE_MONTHS_IN_SECONDS = 60 * 60 * 24 * 90


class RedisService:
    _instance: Optional["RedisService"] = None
    host = REDIS_HOST
    port = REDIS_PORT

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
            cls._instance.redis = redis_client.Redis(host=cls.host, port=cls.port)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "redis"):
            self.redis = redis_client.Redis(host=self.host, port=self.port)

    def set(self, key: str, value: str, ex: int = THREE_MONTHS_IN_SECONDS) -> None:
        self.redis.set(key, json.dumps(value), ex=ex)

    def get(self, key: str):
        cached_data = self.redis.get(key)
        if cached_data is None:
            return None

        return json.loads(cached_data)

    def delete(self, key: str) -> None:
        self.redis.delete(key)
