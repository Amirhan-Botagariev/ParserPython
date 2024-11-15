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
                parser.get_driver().execute_script("window.scrollTo(0, 0);")
                parser.click_heading(heading)
                time.sleep(2)
                final_headings[heading] = parser.get_subheadings()
                time.sleep(2)
                save_json(final_headings[heading], heading)


        return final_headings
def save_json(res, name):
        file_path = os.path.join('/Users/amirhanbotagariev/PycharmProjects/ParserPython/data', f'{name}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False, indent=4)


def scraping():
        parser.open_browser()

        #final_headings = scrape_whole_headings()



        parser.close_browser()

if __name__ == "__main__":
    scraping()