import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from config import BASE_URL


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

    category_info["subtitle"] = {[subtitle, link] for subtitle, link in zip(subtitles, links)}

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
    def open_browser(self):
        self.driver.get(BASE_URL)
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
                    button.click()
                    time.sleep(1)
        except Exception as e: pass

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


