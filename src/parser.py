import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    def change_city(self, need_city):
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
                if city_name.text.strip() == need_city:
                    city_name.click()
                    print(f"Клик выполнен по '{need_city}'")
                    break
                else:
                    print("Элемент с текстом 'Астана' не найден.")
        except Exception as e:
            print(f"Ошибка: {e}")
    def open_browser(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        self.change_city('Астана')
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


