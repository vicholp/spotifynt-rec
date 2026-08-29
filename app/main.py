from fastapi import FastAPI
from .routers import recordings, collections, recommendations, events

app = FastAPI()

app.include_router(recordings.router)
app.include_router(collections.router)
app.include_router(recommendations.router)
app.include_router(events.router)


@app.get("/healthz")
def health():
    return {"status": "ok"}
