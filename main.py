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
    # "https://www.youtube.com/watch?v=vTCImFO_m9A",
    ("https://www.bilibili.com/bangumi/play/ss73355", "S01"),
    ("https://www.bilibili.com/bangumi/play/ss74816", "S02"),
    ("https://www.bilibili.com/bangumi/play/ss74817", "S03"),
    ("https://www.bilibili.com/bangumi/play/ss74818", "S04"),
    ("https://www.bilibili.com/bangumi/play/ss74820", "S05"),
    ("https://www.bilibili.com/bangumi/play/ss74821", "S06"),
    ("https://www.bilibili.com/bangumi/play/ss74822", "S07"),
    ("https://www.bilibili.com/bangumi/play/ss74823", "S08"),
    ("https://www.bilibili.com/bangumi/play/ss74824", "S09"),
    ("https://www.bilibili.com/bangumi/play/ss74826", "S10"),
    ("https://www.bilibili.com/bangumi/play/ss74827", "S11"),
    ("https://www.bilibili.com/bangumi/play/ss74828", "S12"),
]

task_list: list[DownloadTask] = []
for example in example_url:
    url, season = example
    option = deepcopy(example_download_options)
    option["paths"]["home"] = option["paths"]["home"] + "/" + season
    task_list.append(DownloadTask(url, option))

t1 = time()
manager = DownloadManager(example_config)
manager.task_list = task_list
for _ in range(2):
    manager.download()
t2 = time()
print(f"Total time taken: {t2-t1} seconds")
