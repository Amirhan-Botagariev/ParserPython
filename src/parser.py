import math
import re
import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

from config import BASE_URL, CITY


def get_title(category_info, category_div):
    try:
        title = category_div.find_element(By.CSS_SELECTOR,
                                            "p.Typography.CatalogPage_subCategoryTitle__fU8kY.Typography__XL.Typography__XL_Bold")
        category_info["title"] = title.text.strip() if title else None
    except Exception as e:
        category_info["title"] = None

    return category_info
def get_subtitle(category_info, category_div):
    subtitles = []
    links = []

    subtitles_search = category_div.find_elements(By.CSS_SELECTOR, "p.Typography.Typography__M")

    for subtitle in subtitles_search:
        subtitles.append(subtitle.text)

    list_items = category_div.find_elements(By.CSS_SELECTOR, "li")
    for li in list_items:
        try:
            href_search = li.find_element(By.CSS_SELECTOR, "a.CatalogPage_link__rtVT6")
            href = href_search.get_attribute('href')
            links.append(href)
        except:
            continue  # Если ссылки нет, просто пропускаем

    category_info["subtitle"] = {subtitle: link for subtitle, link in zip(subtitles, links)}
    return category_info


class Parser:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Parser, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True

        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)

        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
    def get_driver(self):
        return self.driver
    def change_city(self):
        try:
            modal_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "CitySelector_block__gRcUu"))
            )
            modal_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "CitiesList_listItem__dVrVg"))
            )

            cities = self.driver.find_elements(By.CSS_SELECTOR,
                                                       "div.CitiesList_listItem__dVrVg.CitiesList_major__xzX7M")

            for city in cities:
                city_name = city.find_element(By.CSS_SELECTOR, "p.Typography.CitiesList_name__6yw7D.Typography__Body")
                if city_name.text.strip() == CITY:
                    city_name.click()
                    break
        except Exception as e:
            print(f"Ошибка: {e}")
    def open_browser(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        self.change_city()
        time.sleep(1)
    def close_browser(self):
        self.driver.quit()
    def get_main_headings(self) -> list:
        headings = self.driver.find_element(By.CLASS_NAME, "CatalogPage_firstLevelList__oG8fX") \
            .find_elements(By.TAG_NAME, 'p')
        texts = [val.text for val in headings]

        time.sleep(2)
        return texts
    def get_subheadings(self):
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.CatalogPage_collapseButton__RTqD3")
            for button in buttons:
                if button.is_displayed() and button.is_enabled():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)

                    ActionChains(self.driver).move_to_element(button).click().perform()

                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.CatalogPage_collapseButton__RTqD3"))
                    )
                    time.sleep(1)
                else:
                    pass

        except Exception as e:
            print(e)

        time.sleep(2)

        categories_data = []
        categories_divs = (self.driver.find_element(By.CSS_SELECTOR,
                                           "section.CatalogPage_categories__EwiSr.CatalogPage_categoriesVisible__y3lHh")
                               .find_elements(By.CSS_SELECTOR, "div"))

        for category_div in categories_divs:
            category_info = {}

            category_info = get_title(category_info, category_div)
            category_info = get_subtitle(category_info, category_div)

            # Добавляем данные категории в общий список
            categories_data.append(category_info)

        return categories_data
    def click_heading(self, target_text):
        button = self.driver.find_element(By.XPATH,
                                      f"//p[contains(@class, 'Typography__L_Bold') and text()='{target_text}']")
        button.click()
    def page_numbers(self) -> int:
        try:
            text =self.driver.find_element(By.CSS_SELECTOR, 'div.CategoryPageList_titleWrapper__xcLmA, p.CategoryPageList_subtitle__s70kV').text.split()
            for t in text:
                if t.isdigit():
                    page_number = math.ceil(int(t) / 24)
                    return page_number

        except Exception as e:
            print(e)

        return 1

    def parse_subcategory(self, link):
        self.driver.get(link)
        time.sleep(2)

        page_numbers = self.page_numbers()
        data = dict()
        for page in range(1, page_numbers + 1):
            self.driver.get(link + f'?page={page}')

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR,
                         'article.CategoryPageList_block__PhCqa ul.ProductList_block__nJTj5.CategoryPageList_productList__zMI0I')
                    )
                )
                block = self.driver.find_element(By.CSS_SELECTOR,
                                                 'article.CategoryPageList_block__PhCqa ul.ProductList_block__nJTj5.CategoryPageList_productList__zMI0I')
                cards = block.find_elements(By.CSS_SELECTOR,
                                                  'li.ProductList_item__6LvUK'
                                                  )
                links = []
                for card in cards[:25]:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located(
                                (By.CSS_SELECTOR,
                                 'a.ProductItem_itemLink__cud7j')
                            )
                        )
                        link_element = card.find_element(By.CSS_SELECTOR, 'a.ProductItem_itemLink__cud7j')
                        links.append(link_element.get_attribute("href"))
                    except Exception as e:
                        pass

                for link in links:
                    card_info = self.parse_product_page(link)
                    data[link] = card_info

            except Exception as e:
                pass

            return data

    def parse_product_page(self, link) -> dict:
        self.driver.get(link)
        time.sleep(2)
        card_info = dict()
        def parse_name_and_tags():
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR,
                         'div.ProductInfo_header___fJlQ')
                    )
                )
                name = self.driver.find_element(By.CSS_SELECTOR,
                                                              "div.ProductInfo_header___fJlQ h1.Typography.Typography__XL.Typography__XL_Bold")
                name = name.text

                tags = []
                tag_blocks = self.driver.find_elements(By.CSS_SELECTOR,
                                                               'div.ProductInfo_header___fJlQ div.Stickers_root__La_UR')

                for tag_block in tag_blocks:
                    tags.append(tag_block.text)
            except Exception as e:
                return 'Nan', 'Nan'
            return name, tags
        def parse_color():
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.Variants_block__nmrkp.ProductInfo_variants__KKdAP'))
                )

                block = self.driver.find_element(By.CSS_SELECTOR,
                                                   'div.Variants_block__nmrkp.ProductInfo_variants__KKdAP')

                color_span = block.find_element(By.CSS_SELECTOR,
                                                'h3.Typography.Variants_title__t5f7P.Typography__L.Typography__L_Bold span')
                color = color_span.text.capitalize()

            except Exception as e:
                return 'Nan'
            return color
        def parse_price():
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'div.Carousel_block__TieVp')
                    )
                )

                block = self.driver.find_element(By.CSS_SELECTOR, 'div.ProductActions_wrapper__hdUbd')
                try:
                    newPrice = (
                        (block.find_element(By.CSS_SELECTOR,
                                            'div.ProductPricesVariantB_block__hevXI.ProductActions_price__BnEwP')
                         .find_element(By.CSS_SELECTOR,
                                       'p.Typography.Typography__Heading.Typography__Heading_H1'))
                        .text)
                except NoSuchElementException:
                    newPrice = 'Nan'
                try:
                    oldPrice = (
                        (block.find_element(By.CSS_SELECTOR,
                                            'div.ProductPricesVariantB_block__hevXI.ProductActions_price__BnEwP')
                         .find_element(By.CSS_SELECTOR,
                                       'p.Typography.ProductPricesVariantB_oldPrice__3asPj.Typography__XL'))
                        .text)
                except NoSuchElementException:
                    oldPrice = 'Nan'
            except Exception as e:
                print(e)
                return 'Nan', 'Nan'
            return oldPrice, newPrice
        def parse_barcode():
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'div.Carousel_block__TieVp')
                    )
                )

                block = self.driver.find_element(By.CSS_SELECTOR, 'div.ProductActions_wrapper__hdUbd')

                barcode = (block.find_element(By.CSS_SELECTOR, 'div.ProductActions_ratingGuarantee__kN3uy')
                           .find_element(By.TAG_NAME, 'p')).text
                barcode = int(re.findall(r"\d+", barcode)[0])
            except Exception as e:
                print(e)
                return 'Nan'
            return barcode
        def parse_num_views():
            try:
                block = self.driver.find_element(By.CSS_SELECTOR,
                'div.ViewsCount_viewsCount__Hosc7.ProductInfo_viewsCount__QSn7h')

                num_views = block.find_element(By.CSS_SELECTOR, 'span.Typography.Typography__M').text
            except Exception as e:
                print(e)
                return 'Ошибка'
            return num_views
        def parse_review():
            try:
                block = self.driver.find_element(By.CSS_SELECTOR,
                                                   'div.Carousel_rightTop__dREen')
                star = block.find_element(By.CSS_SELECTOR,
                                          'span.Typography.Rating_rating__XAu4J.Typography__M.Typography__M_Bold').text
                num_of_reviews = block.find_element(By.CSS_SELECTOR,
                                                    'span.Typography.Rating_reviews__Z4rC6.Typography__M').text
                num_of_reviews = re.findall(r"\d+", num_of_reviews)
            except Exception as e:
                print(e)
                return 'Nan', 'Nan'
            return star, num_of_reviews
        def parse_accessibility():
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'div.ProductReviews_list__1m9Qd')
                    )
                )
                block = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'div.ProductReviews_list__1m9Qd')
            except Exception as e:
                print(e)

            def open_more():
                try:
                    button_block = self.driver.find_element(By.CSS_SELECTOR,
                                                              'button.ButtonNext.ButtonNext_Size-L.ButtonNext_Theme-Outline.ProductReviews_showAllLink__7v0_b')
                    button = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//p[contains(@class, "ButtonNext__Text") and text()="Показать все магазины"]')
                        )
                    )
                    button.click()
                except Exception as e:
                    print(e)

            open_more()
            try:
                shop_blocks = self.driver.find_element(By.CSS_SELECTOR,
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
            except Exception as e:
                print(e)
                return 'Ошибка'
            return shops

        card_info['item_name'], card_info['item_tags'] = parse_name_and_tags()
        card_info['item_color'] = parse_color()
        card_info['item_oldPrice'], card_info['item_newPrice'] = parse_price()
        card_info['item_barCode'] = parse_barcode()
        card_info['item_numViews'] = parse_num_views()
        card_info['item_star'], card_info['item_numReviews'] = parse_review()
        card_info['item_store_accessibility'] = parse_accessibility()

        return card_info










