import logging
from argparse import ArgumentParser

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tins.models import Source

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    URL_TO_PARSE = "https://kaczmarski.pl/gielda-wierzytelnosci"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_table_map = {
            "Dłużnik": "company",
            "Nip": "tin",
            "Kwota zadłużenia": "total_amount",
            "Adres": "address",
            "Rodzaj/typ dokumentu stanowiący podstawę dla wierzytelności": "document_type",  # noqa
            "Numer": "number_id",
            "Cena zadłużenia": "sell_for",
        }
        self._start_ts = timezone.now()
        self._init_firefox_driver()

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--tin", type=str, required=True, help="TIN/NIP to find the information."
        )

    def handle(self, *args, **options):
        tin: str = options["tin"]

        try:
            self._load_initial_page()
            self._search_by_tin(tin)
            self._parse_information(tin)
        except WebDriverException as e:
            raise e
        finally:
            self._quit_driver()

    def _init_firefox_driver(self):
        options = Options()
        options.headless = True

        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.cache.disk.enable", True)
        fp.set_preference("browser.cache.memory.enable", True)
        fp.set_preference("browser.cache.offline.enable", False)
        fp.set_preference("network.http.use-cache", True)
        fp.update_preferences()

        path_to_driver = settings.BASE_DIR / "tins/geckodriver"
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

    def _search_by_tin(self, tin: str):
        self._close_overlays_if_exists()
        self._wait_for_loader_to_be_finished()

        search_box = self._driver.find_element(
            By.CLASS_NAME, "ki-market-input"
        ).find_element(By.TAG_NAME, "input")

        search_click_button = self._driver.find_element(
            By.CLASS_NAME, "ki-market-searcher-button"
        )

        search_box.clear()
        search_box.send_keys(tin)
        search_click_button.click()

    def _parse_information(self, tin: str):
        try:
            self._wait_for_loader_to_be_finished()
            self._driver.find_element(By.CLASS_NAME, "ki-market-case")
            self._parse_and_save_success_information()
        except NoSuchElementException:
            logger.info(f"TIN: {tin} Not Found")

    def _parse_and_save_success_information(self):

        more_button = self._web_driver_wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "ki-market-case"))
        )
        more_button.click()

        data = dict()
        soup = BeautifulSoup(self._driver.page_source, "lxml")
        root_tag = soup.find("div", class_="ki-market-case ki-market-case--expanded")

        for child in root_tag.children:
            if child["class"] == ["ki-market-case-header"]:
                for idx, nested_child in enumerate(child.children):
                    if idx < 3:
                        data[
                            nested_child.span.get_text().strip()
                        ] = nested_child.get_text().strip()

            elif child["class"] == ["ki-market-case-details"]:
                for idx, nested_child in enumerate(child.children):
                    if idx < 2:
                        if idx == 0:
                            for idx_1, last_nested_child in enumerate(
                                nested_child.children
                            ):
                                if idx_1 == 0:
                                    data[
                                        last_nested_child.span.get_text().strip()
                                    ] = last_nested_child.div.get_text().strip()
                                else:
                                    data[
                                        last_nested_child.span.get_text().strip()
                                    ] = last_nested_child.get_text().strip()

                        elif idx == 1:
                            data[
                                nested_child.div.span.get_text().strip()
                            ] = nested_child.div.get_text().strip()

        self._save_data(data)

    def _save_data(self, data: dict):
        data_to_save = dict()
        for key, value in data.items():
            if key in self._data_table_map:
                data_to_save[self._data_table_map[key]] = value

        data_to_save["parsing_start_ts"] = self._start_ts
        data_to_save["parsing_end_ts"] = timezone.now()
        Source.objects.create(**data_to_save)

    def _quit_driver(self):
        self._driver.quit()
