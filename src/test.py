from parser import Parser
import pprint
parser = Parser()

# final_headings = {}
# heading1 = parser.get_heading_1()
# heading2 = parser.get_heading_2()
#
# for h1 in heading1:
#         heading2 = parser.get_heading_2()
#         for h2 in heading2:

parser.open_browser()
print(parser.scrape_whole_headings())