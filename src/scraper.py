import time

from src import utils
from src.DataFrame import DataFrame
from src.parser import Parser

parser = Parser()
df = DataFrame()

def scrape_whole_headings() -> dict:
        final_headings = {}
        main_headings = parser.get_main_headings()

        for heading in main_headings:
                parser.get_driver().execute_script("window.scrollTo(0, 0);")
                parser.click_heading(heading)
                time.sleep(2)
                final_headings[heading] = parser.get_subheadings()
                time.sleep(2)
                utils.save_json(final_headings[heading], heading)


        return final_headings
def parse_links(whole_data):
        category = whole_data
        data = dict()
        for section in category:
                title = section['title']
                subtitle = section['subtitle']

                for sub_category, link in subtitle.items():
                        data = parser.parse_subcategory(link)
        return data







def scraping():
        parser.open_browser()
        #final_headings = scrape_whole_headings()

        whole_data = utils.read_json()
        data = parse_links(whole_data)
        print(data)


        parser.close_browser()

if __name__ == "__main__":
    scraping()