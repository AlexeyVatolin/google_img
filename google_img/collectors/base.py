from typing import List

import time
from abc import ABC, abstractmethod

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BaseCollector(ABC):
    def __init__(self, no_gui=False, proxy=None):
        chromedriver_path: str = chromedriver_autoinstaller.install()

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        if no_gui:
            chrome_options.add_argument("--headless")
        if proxy:
            chrome_options.add_argument(f"--proxy-server={proxy}")
        self.browser = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)

        browser_version = "Failed to detect version"
        chromedriver_version = "Failed to detect version"
        major_version_different = False

        if "browserVersion" in self.browser.capabilities:
            browser_version = str(self.browser.capabilities["browserVersion"])

        if "chrome" in self.browser.capabilities:
            if "chromedriverVersion" in self.browser.capabilities["chrome"]:
                chromedriver_version = str(
                    self.browser.capabilities["chrome"]["chromedriverVersion"]
                ).split(" ")[0]

        if browser_version.split(".")[0] != chromedriver_version.split(".")[0]:
            major_version_different = True

        print("_________________________________")
        print(f"Current web-browser version:\t{browser_version}")
        print(f"Current chrome-driver version:\t{chromedriver_version}")
        if major_version_different:
            print("warning: Version different")
            print(
                'Download correct version at "http://chromedriver.chromium.org/downloads" and place in "./chromedriver"'
            )
        print("_________________________________")

    def get_scroll(self):
        pos = self.browser.execute_script("return window.pageYOffset;")
        return pos

    def wait_and_click(self, xpath):
        #  Sometimes click fails unreasonably. So tries to click at all cost.
        try:
            w = WebDriverWait(self.browser, 15)
            elem = w.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            elem.click()
            self.highlight(elem)
        except Exception as e:
            print(f"Click time out - {xpath}")
            print("Refreshing browser...")
            self.browser.refresh()
            time.sleep(2)
            return self.wait_and_click(xpath)

        return elem

    def highlight(self, element):
        self.browser.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            element,
            "background: yellow; border: 2px solid red;",
        )

    @staticmethod
    def remove_duplicates(values):
        return list(dict.fromkeys(values))

    @staticmethod
    def remove_empty(values: List[str]) -> List[str]:
        return [x for x in values if x]

    @abstractmethod
    def collect(self, keyword: str, add_url: str = "") -> List[str]:
        pass

    def __del__(self):
        self.browser.close()
