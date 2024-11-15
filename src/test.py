import time

from selenium.webdriver.common.by import By

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
time.sleep(3)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

try:
    modal_button = WebDriverWait(parser.get_driver(), 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "CitySelector_block__gRcUu"))
    )
    modal_button.click()

    WebDriverWait(parser.get_driver(), 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "CitiesList_listItem__dVrVg"))
    )

    cities = parser.get_driver().find_elements(By.CSS_SELECTOR, "div.CitiesList_listItem__dVrVg.CitiesList_major__xzX7M")

    for city in cities:
        city_name = city.find_element(By.CSS_SELECTOR, "p.Typography.CitiesList_name__6yw7D.Typography__Body")
        if city_name.text.strip() == "Астана":
            city_name.click()
            print("Клик выполнен по 'Астана'")
            break
        else:
            print("Элемент с текстом 'Астана' не найден.")
except Exception as e:
    print(f"Ошибка: {e}")

