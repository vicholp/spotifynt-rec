from pydantic import BaseModel
from ..clients.mongo_client import PyObjectId
from typing import Literal, Optional
from datetime import datetime
from pydantic import Field
from enum import StrEnum

class Session(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: datetime | None = None
    user_id: str | None = None

class ShowedSource(StrEnum):
    RECOMMENDATIONS = "recommendations"
    SEARCH = "search"

class AddedToQueueSource(StrEnum):
    RECOMMENDATIONS = "recommendations"
    SEARCH = "search"

class RecordingAddedToQueueGroup(StrEnum):
    BY_RECORDING = "by_recording"
    BY_RELEASE = "by_release"
    BY_ARTIST = "by_artist"


class EventType(StrEnum):
    RECORDING_PLAY_STARTED = "recording_play_started"
    RECORDING_PLAYED = "recording_played"
    RECORDING_SKIPPED = "recording_skipped"
    RECORDING_SKIPPED_BACKWARD = "recording_skipped_backward"
    RECORDING_SHOWED = "recording_showed"
    RECORDING_ADDED_TO_QUEUE = "recording_added_to_queue"
    RECORDING_REMOVED_FROM_QUEUE = "recording_removed_from_queue"

    RELEASE_ADDED_TO_QUEUE = "release_added_to_queue"
    RELEASE_SHOWED = "release_showed"

    ARTIST_SHOWED = "artist_showed"

    QUEUE_CLEARED = "queue_cleared"
    QUEUE_SHUFFLED = "queue_shuffled"

    SEARCH_PERFORMED = "search_performed"

class RecordingPlayStartedPayload(BaseModel):
    recording_id: int

class RecordingPlayedPayload(BaseModel):
    recording_id: int
    play_duration: int

class RecordingSkippedPayload(BaseModel):
    recording_id: int
    play_duration: int

class RecordingSkippedBackwardPayload(BaseModel):
    recording_id: int
    play_duration: int

class RecordingShowedPayload(BaseModel):
    recording_id: int
    source: ShowedSource

class RecordingAddedToQueuePayload(BaseModel):
    recording_id: int
    source: AddedToQueueSource
    group: RecordingAddedToQueueGroup


class RecordingRemovedFromQueuePayload(BaseModel):
    recording_id: int

class ReleaseAddedToQueuePayload(BaseModel):
    release_id: int
    source: AddedToQueueSource

class ReleaseShowedPayload(BaseModel):
    release_id: int
    source: ShowedSource

class ArtistShowedPayload(BaseModel):
    artist_id: str
    source: ShowedSource

class QueueClearedPayload(BaseModel):
    pass

class QueueShuffledPayload(BaseModel):
    pass

class SearchPerformedPayload(BaseModel):
    query: str



class BaseEvent(BaseModel):
    created_at: datetime | None = None
    user_id: int | None = None
    session_id: str | None = None


class RecordingPlayStartedEvent(BaseEvent):
    event_type: Literal[EventType.RECORDING_PLAY_STARTED]
    payload: RecordingPlayStartedPayload

class RecordingPlayedEvent(BaseEvent):
    event_type: Literal[EventType.RECORDING_PLAYED]
    payload: RecordingPlayedPayload

class RecordingSkippedEvent(BaseEvent):
    event_type: Literal[EventType.RECORDING_SKIPPED]
    payload: RecordingSkippedPayload

class RecordingShowedEvent(BaseEvent):
    event_type: Literal[EventType.RECORDING_SHOWED]
    payload: RecordingShowedPayload

class RecordingAddedToQueueEvent(BaseEvent):
    event_type: Literal[EventType.RECORDING_ADDED_TO_QUEUE]
    payload: RecordingAddedToQueuePayload

class RecordingRemovedFromQueueEvent(BaseEvent):
    event_type: Literal[EventType.RECORDING_REMOVED_FROM_QUEUE]
    payload: RecordingRemovedFromQueuePayload

class ReleaseAddedToQueueEvent(BaseEvent):
    event_type: Literal[EventType.RELEASE_ADDED_TO_QUEUE]
    payload: ReleaseAddedToQueuePayload

class ReleaseShowedEvent(BaseEvent):
    event_type: Literal[EventType.RELEASE_SHOWED]
    payload: ReleaseShowedPayload

class ArtistShowedEvent(BaseEvent):
    event_type: Literal[EventType.ARTIST_SHOWED]
    payload: ArtistShowedPayload

class QueueClearedEvent(BaseEvent):
    event_type: Literal[EventType.QUEUE_CLEARED]
    payload: QueueClearedPayload

class QueueShuffledEvent(BaseEvent):
    event_type: Literal[EventType.QUEUE_SHUFFLED]
    payload: QueueShuffledPayload

class SearchPerformedEvent(BaseEvent):
    event_type: Literal[EventType.SEARCH_PERFORMED]
    payload: SearchPerformedPayload

Event = (
    RecordingPlayStartedEvent |
    RecordingPlayedEvent |
    RecordingSkippedEvent |
    RecordingShowedEvent |
    RecordingAddedToQueueEvent |
    RecordingRemovedFromQueueEvent |
    ReleaseAddedToQueueEvent |
    ReleaseShowedEvent |
    ArtistShowedEvent |
    QueueClearedEvent |
    QueueShuffledEvent |
    SearchPerformedEvent
)
