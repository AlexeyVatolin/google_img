"""
Copyright 2018 YoongiKim

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import List

import time
from abc import ABC, abstractmethod
from pathlib import Path

import chromedriver_autoinstaller
from arsenic import browsers, get_session, keys, services
from arsenic.constants import SelectorType
from arsenic.session import Session

from .collectors import registry


class BaseCollectorAsync(ABC):
    def __init__(self, no_gui=False, proxy=None):
        chromedriver_path: str = chromedriver_autoinstaller.install()

        # chrome_options = Options()
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # if no_gui:
        #     chrome_options.add_argument("--headless")
        # if proxy:
        #     chrome_options.add_argument(f"--proxy-server={proxy}")

        self.service = services.Chromedriver(binary=chromedriver_path)
        self.browser = browsers.Chrome(
            **{"goog:chromeOptions": {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}}
        )

    async def get_scroll(self, session: Session) -> int:
        return await session.execute_script("return window.pageYOffset;")

    @staticmethod
    def remove_duplicates(values):
        return list(dict.fromkeys(values))

    @staticmethod
    def remove_empty(values: List[str]) -> List[str]:
        return [x for x in values if x]

    @abstractmethod
    def collect(self, keyword: str, add_url: str = "") -> List[str]:
        pass


@registry.collector(name="google_full_async")
class GoogleFullCollectorAsync(BaseCollectorAsync):
    async def collect(self, keyword: str, add_url: str = "") -> List[str]:
        print("[Full Resolution Mode]")
        async with get_session(self.service, self.browser) as session:
            await session.get(f"https://www.google.com/search?q={keyword}&tbm=isch{add_url}")
            await session.wait_for_element(5, "input[name=q]")

            body = await session.get_element("body", SelectorType.tag_name)

            first_image = await session.wait_for_element(
                15, '//div[@data-ri="0"]', SelectorType.xpath
            )
            await first_image.click()

            links = []
            count = 1
            last_scroll = 0

            while True:
                try:
                    div_box = await session.get_element(
                        '//div[@id="islsp"]//div[@class="v4dQwb"]', SelectorType.xpath
                    )

                    img = await div_box.get_element('//img[@class="n3VNCb"]', SelectorType.xpath)

                    loading_bar = await div_box.get_element(
                        '//div[@class="k7O2sd"]', SelectorType.xpath
                    )

                    # Wait for image to load. If not it will display base64 code.
                    wait_time = 0
                    while not await loading_bar.get_attribute("style") != "display: none;":
                        time.sleep(0.1)
                        wait_time += 0.1
                        if wait_time > 5:
                            break

                    src = await img.get_attribute("src")

                    if src is not None:
                        yield src
                        print("%d: %s" % (count, src))
                        count += 1
                    if count > 50:
                        break

                except Exception as e:
                    print(f"[Exception occurred while collecting links from google_full] {e}")

                scroll = self.get_scroll(session)
                if scroll == last_scroll:
                    scroll_patience += 1
                else:
                    scroll_patience = 0
                    last_scroll = scroll

                if scroll_patience >= 30:
                    break

                await body.send_keys(keys.RIGHT)

        links = self.remove_duplicates(links)
        links = self.remove_empty(links)

        print(
            "Collect links done. Site: {}, Keyword: {}, Total: {}".format(
                "google_full", keyword, len(links)
            )
        )
