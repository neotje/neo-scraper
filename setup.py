from setuptools import setup, find_packages

PROJECT_NAME = "NeoWebScrapers"
PROJECT_PACKAGE_NAME = "neoscrapers"

PROJECT_GITHUB_USERNAME = "neotje"

PACKAGES = find_packages()

REQUIRED = [
    "aiohttp==3.7.3",
    "cchardet==2.1.7",
    "selenium==3.141.0",
    "openapi-core==0.13.5"
]

setup(
    name=PROJECT_PACKAGE_NAME,
    packages=PACKAGES,
    install_requires=REQUIRED,
    entry_points={"console_scripts": [
        "neoscraper = neoscrapers.__main__:main"]}
)
