from robocorp.tasks import task
import yaml
import time
import datetime
from utils.scraper import NewsScraper
from utils.logging_config import setup_logger



def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


@task
def minimal_task():
    logger = setup_logger("NewsScraper")

    config = load_config("config.yaml")

    search_phrase = config['search_phrase']
    news_category = config['news_category']
    months = config['months']

    # Instanciando a classe NewsScraper
    scraper = NewsScraper(logger)

    try:
        scraper.open_website("https://apnews.com/")
        scraper.search_news(search_phrase)
        scraper.select_news_category(news_category)
        time.sleep(5)

        start_date = scraper.filter_by_date(months)
        articles_list = scraper.extract_article_info(search_phrase)

        # Filtrando artigos por data
        filtered_articles = [article for article in articles_list if
                             (article['timestamp'], datetime.datetime) and article['timestamp'] >= start_date]

        time.sleep(2)
        scraper.save_to_excel(filtered_articles)

        # Fechando o navegador
        scraper.close_browser()
    finally:
        scraper.logger.info("end of script")

if __name__ == "__main__":
    minimal_task()