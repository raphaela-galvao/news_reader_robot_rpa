import re
import shutil
import datetime
import requests
import pandas as pd
from robocorp import browser
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By


class NewsScraper:

    def __init__(self, logger):
        #self.browser = Selenium()

        browser.configure(
            browser_engine="chromium",
            screenshot="only-on-failure",
            headless=True,  # Execute em modo headless para evitar problemas de interface
        )

        self.logger = logger
        self.browser = browser.page()

    def open_website(self, url):
        self.logger.info(f"Abrindo site: {url}")
        self.browser.open_available_browser(url)

    def search_news(self, search_phrase):
        self.logger.info(f"Procurando notícias com a frase: {search_phrase}")
        # wait until the search button is present on the page
        self.browser.wait_until_element_is_visible("css:.SearchOverlay-search-button", timeout=15)

        # click on the search button
        self.browser.click_element("css:.SearchOverlay-search-button")

        # type the search text
        self.browser.input_text("css:.SearchOverlay-search-input", search_phrase)

        # click confirm search
        self.browser.click_element("css:.SearchOverlay-search-submit")

    def select_news_category(self, category):
        self.logger.info(f"Selecionando categoria de notícias: {category}")
        # wait until the category list button is present on the page
        self.browser.wait_until_element_is_visible("css:.SearchFilter-heading", timeout=10)

        # click on the category list button
        self.browser.click_element("css:.SearchFilter-heading")

        # get all items from the category list
        category_items = self.browser.find_elements("css:.SearchFilter-items-item")

        for item in category_items:
            # navigate to the <span> element within the current item
            span_element = self.browser.find_element("css:span", parent=item)
            category_text = self.browser.get_text(span_element).strip()

            if category_text == category:
                self.logger.info(f"Selecionando categoria: {category}")

                # click on the chosen category
                checkbox_element = self.browser.find_element("css:input[type='checkbox']", parent=item)
                checkbox_element.click()
                break

    def filter_by_date(self, months):
        current_date = datetime.datetime.now()
        start_date = current_date - datetime.timedelta(days=30 * months)
        self.logger.info(f"Filtrando notícias de {start_date} até {current_date}")
        return start_date

    def extract_article_info(self, search_phrase):
        self.logger.info("Extraindo informações dos artigos")
        articles = self.browser.find_elements("css:.PageList-items-item")

        article_info = []
        error_messages = []
        counter = 0

        for article in articles:
            try:
                # Title
                try:
                    title_element = article.find_element(By.CSS_SELECTOR,
                                                         ".PageListStandardD .PagePromo-title a.Link span.PagePromoContentIcons-text")
                    title = title_element.text
                except Exception as e:
                    title = None
                    error_messages.append(f"Erro ao extrair o título: {e}")

                # Description
                try:
                    description_element = article.find_element(By.CSS_SELECTOR,
                                                               ".PageListStandardD .PagePromo-description a.Link span.PagePromoContentIcons-text")
                    description = description_element.text
                except Exception as e:
                    description = None
                    error_messages.append(f"Erro ao extrair a descrição: {e}")

                # Timestamp
                try:
                    timestamp_element = article.find_element(By.CSS_SELECTOR,
                                                             ".PageListStandardD .PagePromo-date bsp-timestamp")
                    timestamp = timestamp_element.get_attribute("data-timestamp")
                except Exception as e:
                    timestamp = None
                    error_messages.append(f"Erro ao extrair o timestamp: {e}")

                # Image
                try:
                    image_element = article.find_element(By.CSS_SELECTOR, "img")
                    image_url = image_element.get_attribute("src")
                except Exception as e:
                    image_url = None
                    self.logger.info(f"Erro ao extrair a URL da imagem: {e}")

                if timestamp:
                    counter = counter + 1
                    try:
                        date = self.convert_timestamp_to_american_date(timestamp)
                        phrase_counting = self.count_phrases(title + description, search_phrase)
                        money_counting = self.contains_money(title)
                        image_directory = self.download_images(image_url, counter)

                        article_info.append({
                            "title": title,
                            "description": description,
                            "timestamp": date,
                            "image_url": image_url,
                            f"count_phrases{search_phrase}": phrase_counting,
                            "contains_money": money_counting,
                            "image_directory": image_directory
                        })
                    except ValueError as e:
                        self.logger.info(f"Timestamp inválido: {timestamp}, erro: {e}")
            except Exception as e:
                self.logger.info(f"Erro ao extrair informações do artigo: {e}")
        return article_info

    def convert_timestamp_to_american_date(self, timestamp):
        try:
            timestamp = int(timestamp)
            # dividindo por 1000 para converter de milissegundos para segundos
            timestamp_segundos = timestamp / 1000
            data_hora = datetime.datetime.fromtimestamp(timestamp_segundos)

            print("Data e hora legível:", data_hora)
            return data_hora
        except Exception as e:
            self.logger.info(f"Erro ao converter timestamp: {e}")

    def count_phrases(self, text, phrase):
        return text.lower().count(phrase.lower())

    def save_to_excel(self, article_info, filename='articles.xlsx'):
        df = pd.DataFrame(article_info)
        df.to_excel(filename, index=False)
        self.logger.info(f"Dados salvos em {filename}")

    def contains_money(self, text):
        # Define um padrão para corresponder a valores monetários em vários formatos
        pattern = r'\$\d+(\.\d{1,2})?|\d+ dollars|\d+ USD'

        # Use re.search para encontrar uma correspondência no texto e retornar "True" se uma correspondência for encontrada, caso contrário "False"
        match_found = bool(re.search(pattern, text))

        # Retornar explicitamente "True" ou "False" como strings
        return "True" if match_found else "False"

    def download_images(self, image_url, counter):
        response = requests.get(str(image_url), stream=True)
        directory = f'images/img{counter}.png'

        with open(directory, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        return directory

    def close_browser(self):
        self.browser.close_browser()