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

from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from google_img.collectors import registry

from .base import BaseCollector


@registry.collector(name="google")
class GoogleCollector(BaseCollector):
    def collect(self, keyword: str, add_url: str = "") -> List[str]:
        self.browser.get(
            f"https://www.google.com/search?q={keyword}&source=lnms&tbm=isch{add_url}"
        )

        time.sleep(1)

        print("Scrolling down")

        elem = self.browser.find_element_by_tag_name("body")

        for i in range(60):
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)

        try:
            # You may need to change this. Because google image changes rapidly.
            # btn_more = self.browser.find_element(By.XPATH, '//input[@value="결과 더보기"]')
            # self.wait_and_click('//input[@id="smb"]')
            self.wait_and_click('//input[@type="button"]')

            for i in range(60):
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)

        except ElementNotVisibleException:
            pass

        # //div[@id="islrg"]//img[boolean(@alt)]
        photo_grid_boxes = self.browser.find_elements(By.XPATH, '//div[@class="bRMDJf islir"]')

        print("Scraping links")

        links = []

        for box in photo_grid_boxes:
            try:
                imgs = box.find_elements(By.TAG_NAME, "img")

                for img in imgs:
                    # self.highlight(img)
                    src = img.get_attribute("src")

                    # Google seems to preload 20 images as base64
                    if str(src).startswith("data:"):
                        src = img.get_attribute("data-iurl")
                    links.append(src)

            except Exception as e:
                print(f"[Exception occurred while collecting links from google] {e}")

        links = self.remove_duplicates(links)
        links = self.remove_empty(links)

        print(
            "Collect links done. Site: {}, Keyword: {}, Total: {}".format(
                "google", keyword, len(links)
            )
        )

        return links


@registry.collector(name="google_full")
class GoogleFullCollector(BaseCollector):
    def collect(self, keyword: str, add_url: str = "") -> List[str]:
        print("[Full Resolution Mode]")

        self.browser.get(f"https://www.google.com/search?q={keyword}&tbm=isch{add_url}")
        time.sleep(1)

        elem = self.browser.find_element_by_tag_name("body")

        print("Scraping links")

        self.wait_and_click('//div[@data-ri="0"]')
        time.sleep(1)

        links: List[str] = []
        count = 1

        last_scroll = 0
        scroll_patience = 0

        while True:
            try:
                div_box = self.browser.find_element(
                    By.XPATH, '//div[@id="islsp"]//div[@class="v4dQwb"]'
                )
                self.highlight(div_box)

                img = div_box.find_element(By.XPATH, '//img[@class="n3VNCb"]')
                self.highlight(img)

                loading_bar = div_box.find_element(By.XPATH, '//div[@class="k7O2sd"]')

                # Wait for image to load. If not it will display base64 code.
                while str(loading_bar.get_attribute("style")) != "display: none;":
                    time.sleep(0.1)

                src = img.get_attribute("src")

                if src is not None:
                    links.append(src)
                    # yield src
                    print("%d: %s" % (count, src))
                    count += 1
                if count > 50:
                    break

            except StaleElementReferenceException:
                # print('[Expected Exception - StaleElementReferenceException]')
                pass
            except Exception as e:
                print(f"[Exception occurred while collecting links from google_full] {e}")

            scroll = self.get_scroll()
            if scroll == last_scroll:
                scroll_patience += 1
            else:
                scroll_patience = 0
                last_scroll = scroll

            if scroll_patience >= 30:
                break

            elem.send_keys(Keys.RIGHT)

        links = self.remove_duplicates(links)
        links = self.remove_empty(links)

        print(
            "Collect links done. Site: {}, Keyword: {}, Total: {}".format(
                "google_full", keyword, len(links)
            )
        )

        return links
