import asyncio
import base64
from pathlib import Path
from urllib import parse

import aiofiles
import aiohttp

from google_img.collectors.base import BaseCollector

from .collectors.registry import collector


def download_async(
    keywords: str, output_folder: Path, collector_name: str = "google_full", hidden: bool = True
) -> None:
    image_collector: BaseCollector = collector.registry[collector_name](hidden=hidden)

    for keyword in keywords.split(","):
        asyncio.run(
            download_links_async(keyword.strip(), output_folder, image_collector, collector_name)
        )


async def download_links_async(
    keyword: str, download_path: Path, collector: BaseCollector, collector_name: str
) -> None:
    folder = download_path / keyword
    folder.mkdir(parents=True, exist_ok=True)

    links = collector.collect(keyword)

    async with aiohttp.ClientSession() as session:
        tasks = []
        tasks = [
            place_file(session, link, folder, index, collector_name)
            for index, link in enumerate(links)
        ]
        await asyncio.gather(*tasks)


async def place_file(
    session: aiohttp.ClientSession, source: str, folder: Path, index: int, collector_name: str
) -> None:
    extension = get_extension_from_link(source)
    file_name = f"{collector_name}_{str(index).zfill(4)}{extension}"
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


def base64_to_object(base64_url: str) -> bytes:
    _, encoded = base64_url.split(",", 1)
    data = base64.urlsafe_b64decode(encoded)
    return data


def get_extension_from_link(link: str, default: str = ".jpg") -> str:
    if link.startswith("data:image/jpeg;base64"):
        return ".jpg"
    if link.startswith("data:image/png;base64"):
        return ".png"
    path = parse.urlparse(link).path
    return Path(path).suffix or default
