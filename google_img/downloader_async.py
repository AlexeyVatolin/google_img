import asyncio
import time
from pathlib import Path

import aiofiles
import aiohttp

from google_img.collectors.base import BaseCollector
from google_img.downloader import base64_to_object, get_extension_from_link

from .collectors.registry import collector


def download_async(keywords: str, download_type: str = "google_full") -> None:
    image_collector: BaseCollector = collector.registry[download_type]()

    for keyword in keywords.split(","):
        asyncio.run(
            download_links_async(keyword.strip(), Path("temp_async"), image_collector), debug=True
        )
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    print(f"Completed in {t2-t1} seconds.")


async def download_links_async(
    keyword: str, download_path: Path, collector: BaseCollector
) -> None:
    folder = download_path / keyword
    folder.mkdir(parents=True, exist_ok=True)

    links = collector.collect(keyword)

    async with aiohttp.ClientSession() as session:
        tasks = []
        # index = 0
        # async for link in links:
        #     tasks.append(place_file(session, link, folder, index))
        #     index += 1
        tasks = [place_file(session, link, folder, index) for index, link in enumerate(links)]
        await asyncio.gather(*tasks)


async def place_file(
    session: aiohttp.ClientSession, source: str, folder: Path, index: int
) -> None:
    extension = get_extension_from_link(source)
    file_name = f"google_{str(index).zfill(4)}{extension}"
    file_path = folder / file_name
    if source.startswith("data:image"):
        response_bytes = base64_to_object(source)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(response_bytes)
            await f.flush()
    else:
        response = await session.get(source, ssl=False)

        async with aiofiles.open(file_path, "wb") as f:
            async for data in response.content.iter_any():
                await f.write(data)
