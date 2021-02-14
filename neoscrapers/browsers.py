import logging

from selenium import webdriver

_LOGGER = logging.getLogger(__name__)

_active_browsers = []
_max_browsers = 5

async def get_browser() -> webdriver.Chrome:
    while len(_active_browsers) == _max_browsers:
        pass
    
    driver = webdriver.Chrome()
    _active_browsers.append(driver)
    _LOGGER.info(f"browser count: {len(_active_browsers)}")
    return driver

async def return_browser(driver: webdriver.Chrome):
    if driver in _active_browsers:
        driver.quit()
        _active_browsers.remove(driver)