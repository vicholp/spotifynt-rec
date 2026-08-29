from pymongo import MongoClient
import logging
from typing import Annotated
from pydantic import BeforeValidator

from ..config import MONGO_HOST, MONGO_DB, MONGO_PASSWORD, MONGO_USERNAME

PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoDB:
    def __init__(self):
        self.client = MongoClient(
            host=MONGO_HOST,
            port=27017,
            username=MONGO_USERNAME,
            password=MONGO_PASSWORD,
        )

        self.db = self.client[MONGO_DB]
        logging.info("Connected to MongoDB")
