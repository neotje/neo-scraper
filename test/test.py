from neoscrapers.scrapers.jumbo import JumboScraper
import threading

def print_progress(v):
    print(v)

scraper = JumboScraper()
scraper.progress.subscribe(print_progress)

scraper.run()
