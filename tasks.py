import time
import yaml
import datetime
from utils.scraper import NewsScraper
from utils.logging_config import setup_logger


def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    logger = setup_logger("NewsScraper")

    config = load_config("config.yaml")

    search_phrase = config['search_phrase']
    news_category = config['news_category']
    months = config['months']

    # instanciando a classe NewsScraper
    scraper = NewsScraper(logger)

    try:
        scraper.open_website("https://apnews.com/")
        scraper.search_news(search_phrase)
        scraper.select_news_category(news_category)
        time.sleep(5)

        start_date = scraper.filter_by_date(months)
        articles_list = scraper.extract_article_info(search_phrase)

        # filtrando artigos por data
        filtered_articles = [article for article in articles_list if article['timestamp'] >= start_date]

        time.sleep(2)
        scraper.save_to_excel(filtered_articles)

        # fechar navegador
        scraper.close_browser()
    finally:
        logger.info("Fim do script")
