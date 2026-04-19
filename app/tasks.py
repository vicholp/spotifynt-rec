from celery import Celery
from typing import Optional
from app.services.downloader_service import DownloaderService
from app.config import CELERY_BROKER_URL

app = Celery("tasks", broker=CELERY_BROKER_URL)


@app.task
def download_video_task(
    url: str, metadata: Optional[dict] = None, webhook_url: Optional[str] = None
):
    downloader_service = DownloaderService()

    try:
        downloader_service.download(url, metadata, webhook_url)
    except Exception as e:
        raise Exception(f"Failed to download video {url}: {str(e)}")
