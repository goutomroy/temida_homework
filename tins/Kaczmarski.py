import logging
import re

from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tins.models import Source, validate_tin

logger = logging.getLogger(__name__)


class GetTextExtractor:
    def __init__(self, element):
        key_value_list = element.get_text("--", strip=True).split("--")
        self.key = key_value_list[0]
        self.value = key_value_list[1]


class Kaczmarski:

    URL_TO_PARSE = "https://kaczmarski.pl/gielda-wierzytelnosci"
    DATA_TABLE_MAP = {
        "Dłużnik": "company",
        "Nip": "tin",
        "Kwota zadłużenia": "total_amount",
        "Adres": "address",
        "Rodzaj/typ dokumentu stanowiący podstawę dla wierzytelności": "document_type",  # noqa
        "Najstarsza data wymagalności w sprawie": "start_ts",
        "Numer": "number_id",
        "Cena zadłużenia": "sell_for",
    }

    def __init__(self, tin):
        self.original_tin = tin
        self.tin = self._validate_and_extract_tin(tin)
        self._parsing_ts = timezone.now()

        self._init_firefox_driver()

    def _validate_and_extract_tin(self, tin):
        validate_tin(tin)
        return re.findall("[0-9]{5,10}", tin)[0]

    def parse_tin(self):
        raw_parsed_data = None
        try:
            self._load_initial_page()
            self._search_by_tin()
            raw_parsed_data = self._parse_information()
        except WebDriverException as e:
            raise e
        finally:
            self._quit_driver()
            return raw_parsed_data

    def _init_firefox_driver(self):
        options = Options()
        options.headless = True

        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.cache.disk.enable", True)
        fp.set_preference("browser.cache.memory.enable", True)
        fp.set_preference("browser.cache.offline.enable", False)
        fp.set_preference("network.http.use-cache", True)
        fp.update_preferences()

        path_to_driver = settings.BASE_DIR / "tins" / "geckodriver"
        self._driver = webdriver.Firefox(
            executable_path=path_to_driver, options=options, firefox_profile=fp
        )
        self._driver.maximize_window()
        self._web_driver_wait = WebDriverWait(self._driver, 10)

    def _load_initial_page(self):
        self._driver.get(self.URL_TO_PARSE)
        self._close_overlays_if_exists()
        self._accept_cookies()

    def _accept_cookies(self):
        try:
            accept_cookie = self._driver.find_element(
                By.XPATH, "//*[@class='wh-cookieInfoBox']/a"
            )
            accept_cookie.click()
        except NoSuchElementException:
            pass

    def _close_overlays_if_exists(self):
        self._close_overlay_by_class_name("wh-popUp-close")

    def _close_overlay_by_class_name(self, class_name: str):
        try:
            close_element = self._driver.find_element(By.CLASS_NAME, class_name)
            close_element.click()
        except NoSuchElementException:
            pass

    def _wait_for_loader_to_be_finished(self):
        try:
            class_name = "ki-loader"
            self._driver.find_element(By.CLASS_NAME, class_name)
            self._web_driver_wait.until(
                EC.invisibility_of_element_located((By.CLASS_NAME, class_name))
            )
        except NoSuchElementException:
            pass

    def _search_by_tin(self):
        self._close_overlays_if_exists()
        self._wait_for_loader_to_be_finished()

        search_box = self._driver.find_element(
            By.CLASS_NAME, "ki-market-input"
        ).find_element(By.TAG_NAME, "input")

        search_click_button = self._driver.find_element(
            By.CLASS_NAME, "ki-market-searcher-button"
        )

        search_box.clear()
        search_box.send_keys(self.tin)
        search_click_button.click()

    def _parse_information(self):
        try:
            self._wait_for_loader_to_be_finished()
            self._driver.find_element(By.CLASS_NAME, "ki-market-case")
            return self._parse_success_information()
        except NoSuchElementException:
            return {"detail": f"TIN: {self.tin} Not Found"}

    def _expand_more(self):
        more_button = self._web_driver_wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "ki-market-case"))
        )
        more_button.click()

    def _parse_success_information(self):
        self._expand_more()

        data = dict()
        soup = BeautifulSoup(self._driver.page_source, "lxml")
        root_tag = soup.find("div", class_="ki-market-case ki-market-case--expanded")

        for child in root_tag.children:
            if child["class"] == ["ki-market-case-header"]:
                for idx, nested_child in enumerate(child.children):
                    if idx < 3:
                        text_extractor = GetTextExtractor(nested_child)
                        data[text_extractor.key] = text_extractor.value

            elif child["class"] == ["ki-market-case-details"]:
                for idx, nested_child in enumerate(child.children):
                    if idx < 2:
                        if idx == 0:
                            for idx_1, last_nested_child in enumerate(
                                nested_child.children
                            ):
                                text_extractor = GetTextExtractor(last_nested_child)
                                data[text_extractor.key] = text_extractor.value

                        elif idx == 1:
                            text_extractor = GetTextExtractor(nested_child)
                            data[text_extractor.key] = text_extractor.value

        self._save_to_db(data)
        return data

    def _save_to_db(self, data: dict):
        data_to_save = dict()
        for key, value in data.items():
            if key in self.DATA_TABLE_MAP:
                data_to_save[self.DATA_TABLE_MAP[key]] = value

        data_to_save["tin"] = self.original_tin
        data_to_save["parsing_ts"] = self._parsing_ts
        data_to_save["start_ts"] = timezone.datetime.strptime(
            data_to_save["start_ts"], "%d-%m-%Y"
        ).strftime("%Y-%m-%d")

        Source.objects.update_or_create(data_to_save, tin=data_to_save["tin"])

    def _quit_driver(self):
        self._driver.quit()
