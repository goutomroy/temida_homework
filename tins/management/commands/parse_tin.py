import logging
import time
from argparse import ArgumentParser

# from Screenshot import Screenshot_Clipping
from bs4 import BeautifulSoup
from django.conf import settings
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from django.core.management import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    URL_TO_PARSE = "https://kaczmarski.pl/gielda-wierzytelnosci"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_firefox_driver()

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--tin", type=str, default=None)

    def handle(self, *args, **options):
        tin: str = options["tin"]

        try:
            self._load_initial_page()
            # self._save_screenshot("s_load_initial_page.png")

            self._search_by_tin(tin)
            # self._save_screenshot("s_after_search_by_tin.png")

            self._click_to_more()
            # self._save_screenshot("s_after_click_to_more.png")
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

    def _click_to_more(self):
        self._wait_for_loader_to_be_finished()
        more_button = self._web_driver_wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "ki-market-case"))
        )
        more_button.click()

    def _parse_information(self, tin: str):
        try:
            self._driver.find_element(
                By.CLASS_NAME, "ki-market-message"
            )
            logger.info(f"TIN: {tin} Not Found")
        except NoSuchElementException:
            self._parse_success_information()

    def _parse_success_information(self):
        soup = BeautifulSoup(self._driver.page_source, "lxml")

    def _save_screenshot(self, file_name):
        self._driver.save_screenshot(file_name)

    def _quit_driver(self):
        self._driver.quit()

    # def _remove_accept_cookie(self):
    #     self._remove_element_by_class_name_from_driver("wh-cookieInfoBox")
    #
    # def _remove_element_by_class_name_from_driver(self, class_name: str):
    #     self._web_driver_wait.until(
    #         EC.visibility_of_element_located((By.CLASS_NAME, class_name))
    #     )
    #
    #     js = (
    #         """
    #         var element = document.querySelector("""
    #         + "'."
    #         + class_name
    #         + "'"
    #         + """);
    #         if (element)
    #             element.remove();
    #         """
    #     )
    #     self._driver.execute_script(js)
