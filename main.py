from pprint import pprint
import subprocess
import os
from typing import Any
from yt_dlp import YoutubeDL  # type: ignore
from typing import Literal, TypedDict


class Config(TypedDict):
    max_retries: int
    # can I use something else to config?


# cSpell: words ytdlp
class DownloadTask:

    def __init__(
        self,
        url: str,
        ytdlp_options: dict,
        priority: Literal[1, 2, 3, 4, 5] = 3,
    ) -> None:
        self.url = url
        self.ytdlp_options: dict = ytdlp_options
        self.priority: Literal[1, 2, 3, 4, 5] = priority


class Processor:
    def __init__(self, config: Config) -> None:
        self.config = config

    def download(self, task: DownloadTask) -> None:
        failure_count = 0
        max_retries = self.config["max_retries"]
        for _ in range(max_retries):
            try:
                with YoutubeDL(task.ytdlp_options) as ydl:
                    info_result = ydl.extract_info(task.url, download=True)
                    assert isinstance(
                        info_result, dict
                    ), "Expected info to be a dictionary"
                    info: dict[str, Any] = info_result
                    return None
            except Exception as e:
                failure_count += 1
                print(f"Error downloading video: {e}")
                if failure_count >= max_retries:
                    print("Max retries reached. Exiting.")


class DownloadManager:
    def __init__(self) -> None:
        pass


# Step 1: Download only, with minimal processing
# cSpell: disable
example_download_options = {
    "format": "bestvideo+bestaudio",  # Get best quality
    "outtmpl": "%(title)s.%(ext)s",  # Simple filename for processing
    "cookiesfrombrowser": ("edge",),
    "merge_output_format": "mp4",  # Just merge the streams
    "postprocessors": [],  # No post-processing yet
    "paths": {
        # "home": "/media/Saz/Backup/MediaStorage/TheBigBangTheory",    # Specified directory
        "temp": os.path.join(os.getcwd(), "download/"),  # Current dir under download/
    },
}

example_config: Config = {
    "max_retries": 3,
}

example_url = [
    "https://www.youtube.com/watch?v=vTCImFO_m9A",
    # "https://www.bilibili.com/bangumi/play/ss73355",
]

task_list = map(lambda url: DownloadTask(url, example_download_options), example_url)
for task in task_list:
    print(f"Processing URL: {task.url}")
    processor = Processor(example_config)
    processor.download(task)
    print(f"Finished processing URL: {task.url}")
