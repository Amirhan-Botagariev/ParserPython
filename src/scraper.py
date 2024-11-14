import json
import os
import time
from pprint import pprint
import pandas as pd
from parser import Parser

parser = Parser()
df = pd.DataFrame()

def scrape_whole_headings() -> dict:
        final_headings = {}
        main_headings = parser.get_main_headings()

        for heading in main_headings:
                try:
                        parser.click_heading(heading)
                        time.sleep(1)
                        final_headings[heading] = parser.get_subheadings()
                except Exception as e:
                        pass

        return final_headings

def save_json(res):
        file_path = os.path.join('/Users/amirhanbotagariev/PycharmProjects/ParserPython/data', 'data.json')
        with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False, indent=4)



def scraping():
        parser.open_browser()

        final_headings = scrape_whole_headings()
        print(final_headings)

        parser.close_browser()

if __name__ == "__main__":
    scraping()