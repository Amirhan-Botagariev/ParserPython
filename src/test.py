import re
import time
from multiprocessing.connection import address_type
from pprint import pformat

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from parser import Parser
parser = Parser()

parser.open_browser()
time.sleep(1)

link = 'https://www.technodom.kz/astana/p/smartfon-gsm-samsung-sm-a556ezkaskz-galaxy-a55-5g-128gb-awesome-navy-279425'
parser.get_driver().get(link)
time.sleep(2)

try:
    WebDriverWait(parser.driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div.ProductReviews_list__1m9Qd')
        )
    )
    block = parser.driver.find_element(
        By.CSS_SELECTOR,
        'div.ProductReviews_list__1m9Qd')
except Exception as e:
    print(e)


def open_more():
    try:
        button_block = parser.driver.find_element(By.CSS_SELECTOR, 'button.ButtonNext.ButtonNext_Size-L.ButtonNext_Theme-Outline.ProductReviews_showAllLink__7v0_b')
        button = WebDriverWait(parser.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//p[contains(@class, "ButtonNext__Text") and text()="Показать все магазины"]')
            )
        )
        button.click()
    except Exception as e:
        print(e)


open_more()
try:
    shop_blocks = parser.driver.find_element(By.CSS_SELECTOR,
                                      'div.StocksList_block__NoKXk')
    shop_blocks = shop_blocks.find_elements(By.CSS_SELECTOR,
                                            'div.StocksList_contentBlock__OVJlO')
    shops = {}
    i = 1
    for block in shop_blocks[1:]:
        info = {}
        address_block = block.find_element(By.CSS_SELECTOR,
                                          'div.StocksList_blockText__VJESN.StocksList_withDescText__tFQrJ')
        info['address'] = address_block.find_element(By.CSS_SELECTOR,
                                                     'p.Typography.Typography__M.Typography__M_Bold').text
        info['detailed_address'] = address_block.find_element(By.CSS_SELECTOR,
                                                              'p.Typography.StocksList_blockDescription__IyAG1.Typography__M').text
        info['working_time'] = block.find_element(By.CSS_SELECTOR,
                                                           'p.Typography.StocksList_blockText__VJESN.StocksList_workHours__hOulU.Typography__M').text
        info['ready_time'] = block.find_element(By.CSS_SELECTOR,
                                                         'p.Typography.StocksList_blockText__VJESN.StocksList_alignText__Cn_8_.Typography__M').text
        info['ready_status'] = block.find_element(By.CSS_SELECTOR,
                                                           'p.Typography.StocksList_blockText__VJESN.StocksList_countLabel__cWNa6.Typography__M.Typography__M_Bold').text
        shops[f'Shop {i}'] = info
        i += 1
    print(shops)
except Exception as e:
    print(e)

