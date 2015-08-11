from scraper.scraper import scrap_and_dump
import logging



logging.basicConfig(filename='run_scraper.log')
scrap_and_dump('recorded_html_07_08')

