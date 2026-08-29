from fastapi import APIRouter
from app.clients.qdrant_client import QdrantService
from pydantic import BaseModel
from ..schemas.event_schema import Event
from ..clients.mongo_client import MongoDB

router = APIRouter(
    prefix="/events",
    responses={404: {"description": "Not found"}},
    tags=["events"],
)

class CreateEventsRequest(BaseModel):
    events: list[Event]


@router.post("/batch")
def create_events(request: CreateEventsRequest):
    mongo_service = MongoDB()
    events_collection = mongo_service.db["events"]

    events_collection.insert_many([event.dict(by_alias=True) for event in request.events])

    return {"message": "Events created"}
