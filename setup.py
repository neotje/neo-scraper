from setuptools import setup, find_packages
import os

PROJECT_NAME = "NeoWebScrapers"
PROJECT_PACKAGE_NAME = "neoscrapers"

PROJECT_GITHUB_USERNAME = "neotje"

PACKAGES = find_packages()

REQUIRED = [
    "aiohttp==3.7.3",
    "cchardet==2.1.7",
    "selenium==3.141.0",
    "openapi-core==0.13.5",
    "aiohttp-session==2.9.0",
    "cryptography==3.3.1",
    "python-magic==0.4.18",
    "beautifulsoup4==4.9.3",
    "requests==2.25.1",
    "html5lib==1.1"
]

setup(
    name=PROJECT_PACKAGE_NAME,
    packages=PACKAGES,
    install_requires=REQUIRED,
    entry_points={"console_scripts": [
        "neoscraper = neoscrapers.__main__:main"]}
)
