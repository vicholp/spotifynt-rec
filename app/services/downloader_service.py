import os
from .yt_dlp_service import YtDlpService
from .minio_service import MinioService
from .webhook_service import WebhookService
from .redis_service import RedisService

from typing import Optional
import logging


class DownloaderService:
    def download(
        self,
        url: str,
        metadata: Optional[dict] = None,
        webhook_url: str | None = None,
        force_download: bool = False,
    ) -> str | None:
        yt_dlp_service = YtDlpService()
        minio_service = MinioService()
        backend_service = WebhookService()

        try:
            if not force_download:
                cached_path = RedisService().get(url)

                if cached_path:
                    if webhook_url:
                        backend_service.finish_download(
                            webhook_url, url, cached_path, metadata
                        )

                    if cached_path:
                        return cached_path

            video_url = url

            file_path = yt_dlp_service.download(video_url)
            if not file_path:
                if webhook_url:
                    backend_service.finish_download(
                        webhook_url, url, "", metadata, "error1"
                    )

                return None

            minio_path = minio_service.upload_file(file_path)

            if not minio_path:
                if webhook_url:
                    backend_service.finish_download(
                        webhook_url, url, "", metadata, "error3"
                    )

                return None

            if webhook_url:
                backend_service.finish_download(webhook_url, url, minio_path, metadata)

            os.remove(file_path)

            RedisService().set(url, minio_path)

            return minio_path

        except Exception as e:
            logging.exception("Error downloading video")
            logging.error(f"Error details: {e}")

            if webhook_url:
                backend_service.finish_download(
                    webhook_url, url, "", metadata, "error2"
                )

        return None
