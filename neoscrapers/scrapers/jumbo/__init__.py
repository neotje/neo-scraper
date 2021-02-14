"""Jumbo scraper"""
import logging
from time import sleep

from neoscrapers.helpers.types import Scraper
from neoscrapers.helpers.util import Observable
from neoscrapers.output import OutputManager
from neoscrapers import browsers


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

import re
import requests
from bs4 import BeautifulSoup

import csv


_LOGGER = logging.getLogger(__name__)

NAME = "jumbo"

async def setup(manager):
    await manager.register_scraper(NAME, JumboScraper)


class JumboScraper(Scraper):
    def __init__(self):
        self._progress = Observable(0)
        self._output = OutputManager().get_output(NAME, "csv")

    @property
    def progress(self):
        return self._progress

    @property
    def name(self):
        return NAME

    @property
    def output(self):
        return self._output

    async def run(self):
        driver = await browsers.get_browser()
        driver.get("https://www.jumbo.com/winkels")

        wait = WebDriverWait(driver, 5)

        # get all stores button and click on it
        btn = driver.find_element_by_id("stores-all")
        btn.click()

        # get array of li elements
        wait.until(presence_of_element_located(
            (By.CSS_SELECTOR, "#jum-store-list > ul > li")))
        liArr = driver.find_elements_by_css_selector("#jum-store-list > ul > li")

        # get all store names and address
        data = []
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}

        len_liArr = len(liArr)
        for i in range(0, len_liArr):
            li = liArr[i]
            await self._progress.next(i/len_liArr)

            winkel = li.find_element(By.TAG_NAME, "h3").text
            # print(winkel)

            # format name to path.
            path = re.sub("( )+", "_", winkel)
            path = re.sub("\W+", "", path)
            path = re.sub("_+", "-", path).lower()

            # get page content.
            req = requests.get("https://www.jumbo.com/winkel/" + path, headers=headers)

            # check if page exists.
            if not req.status_code == 200:
                # if not get address without postal code.
                print("does not have it's own page. getting adress without postal code..")

                soup = BeautifulSoup(li.get_attribute('innerHTML'), "html5lib")

                strArr = []
                for s in soup.stripped_strings:
                    strArr.append(str(s).replace(u'\xa0', ' '))

                # add row
                row = {"winkel": winkel, "straat": strArr[1], "plaats": strArr[2]}
                data.append(row)
                continue

            # get adress from store page.
            soup = BeautifulSoup(req.text, "html5lib")
            a = soup.find_all("a", attrs={"title": "Bekijk op de kaart"})[0]

            strArr = []
            for s in a.stripped_strings:
                strArr.append(str(s).replace(u'\xa0', ' '))

            # add row
            row = {"winkel": winkel, "straat": strArr[0], "plaats": strArr[1]}
            data.append(row)

        with self._output.open() as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["winkel", "straat", "plaats"])
            writer.writeheader()
            writer.writerows(data)

        await browsers.return_browser(driver)

        await self._progress.next(1)
