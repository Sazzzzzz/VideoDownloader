from pprint import pprint
import subprocess
import os
from typing import Any
from yt_dlp import YoutubeDL  # type: ignore
from typing import Literal, TypedDict
from time import sleep, time
from copy import deepcopy
import json


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
                wait_time = 2**failure_count
                print(f"Retrying in {wait_time} seconds...")
                sleep(wait_time)
                if failure_count >= max_retries:
                    print("Max retries reached. Exiting.")
        else:
            print("Download failed after max retries.")
            files = os.listdir(task.ytdlp_options["paths"]["temp"])
            for file in files:
                os.remove(os.path.join(task.ytdlp_options["paths"]["temp"], file))
            print("Removed partial files.")
            return None


class DownloadManager:
    def __init__(self, config: Config) -> None:
        self.task_list: list[DownloadTask] = []
        self.config = config

    def download(self) -> None:
        for task in self.task_list:
            print(f"Processing URL: {task.url}")
            processor = Processor(self.config)
            processor.download(task)
            print(f"Finished processing URL: {task.url}")
        self.task_list.clear()


# Step 1: Download only, with minimal processing
# cSpell: disable
example_download_options = {
    "format": "bestvideo+bestaudio",  # Get best quality
    "outtmpl": "%(title)s.%(ext)s",  # Simple filename for processing
    "cookiesfrombrowser": ("firefox",),
    "merge_output_format": "mp4",  # Just merge the streams
    "postprocessors": [],  # No post-processing yet
    "paths": {
        "home": "/media/Saz/Backup/MediaStorage/TheBigBangTheory",  # Specified directory
        "temp": os.path.join(os.getcwd(), "download/"),  # Current dir under download/
    },
}
with open("config.json", "r") as f:
    example_config: Config = json.load(f)
print(example_config["max_retries"])

example_url = [
    "https://www.bilibili.com/video/BV18wLUzgE23/",
    # "https://www.bilibili.com/bangumi/play/ss73355",
]

task_list = map(lambda url: DownloadTask(url, example_download_options), example_url)
for task in task_list:
    print(f"Processing URL: {task.url}")
    processor = Processor(example_config)
    processor.download(task)
    print(f"Finished processing URL: {task.url}")
