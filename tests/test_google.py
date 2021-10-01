from pathlib import Path

import pytest

from google_img.downloader_async import download_async


@pytest.mark.parametrize("keywords", (["dog"]))
def test_google(tmpdir, keywords):
    output_folder = Path(tmpdir)
    download_async(keywords=keywords, collector_name="google", output_folder=output_folder)

    assert (
        output_folder / keywords
    ).exists(), f"Folder with keywords '{keywords}' images does not exists"

    assert (
        len(list((output_folder / keywords).iterdir())) > 0
    ), f"Folder with keywords '{keywords}' images are empty"
