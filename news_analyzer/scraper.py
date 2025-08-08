import re
import time
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

URL_BASE = "https://www.otempo.com.br"


def _setup_driver(headless: bool = True):
    """Initializes and returns a Selenium WebDriver instance."""
    firefox_driver_path = GeckoDriverManager().install()
    service = Service(executable_path=firefox_driver_path)
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Firefox(service=service, options=options)
    return driver


def _scrape_article_details(driver, article_url: str):
    """
    Navigates to a single article URL and scrapes its details.

    Args:
        driver: The Selenium WebDriver instance.
        article_url: The URL of the article to scrape.

    Returns:
        A dictionary containing the scraped details of the article.
    """
    details = {
        'data_pura': "Erro",
        'horario': "Erro",
        'texto_completo': "Erro ao coletar texto",
        'link_imagem_principal': "Erro ao coletar imagem",
        'tem_video': False,
        'nome_reporter': "Erro ao coletar repórter",
        'tags_noticia': "Erro ao coletar tags"
    }
    try:
        driver.get(article_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cp023-assinatura-do-artigo'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Reporter
        author_info_div = soup.find('div', class_='cmp__author-info')
        if author_info_div:
            author_name_span = author_info_div.find('span', class_='cmp__author-name')
            if author_name_span:
                nome_reporter_raw = author_name_span.get_text(strip=True)
                nome_reporter = re.sub(r'^(Por|Redação)\s*', '', nome_reporter_raw, flags=re.IGNORECASE).strip()
                details['nome_reporter'] = ' '.join(nome_reporter.split())

        # Date and Time
        publication_span = soup.find('span', class_='cmp__author-publication')
        if publication_span and publication_span.span:
            data_str = publication_span.span.get_text(strip=True).split(' - ')[0].strip()
            if '|' in data_str:
                parts = data_str.split('|')
                details['data_pura'] = parts[0].strip()
                details['horario'] = parts[1].strip()
            else:
                details['data_pura'] = data_str
                details['horario'] = "N/A"

        # Full Text
        text_div = soup.find('div', class_='read-controller materia__tts article-whole article-body')
        if text_div:
            paragrafos = text_div.find_all('p')
            details['texto_completo'] = '\n'.join([p.get_text(strip=True) for p in paragrafos if p.get_text(strip=True)])

        # Main Image
        gallery_container = soup.find('div', class_='gallery__container gallery_highlight')
        if gallery_container:
            img_tag = gallery_container.find('img', class_='gallery__image')
            if img_tag and 'src' in img_tag.attrs:
                details['link_imagem_principal'] = urljoin(URL_BASE, img_tag['src'])

        # Video
        if soup.find('iframe', class_='c-video__frame') or soup.find('video'):
            details['tem_video'] = True
        else:
            news_body = soup.find('div', class_='c-news-body')
            if news_body and news_body.find('iframe', src=re.compile(r"youtube\.com|vimeo\.com|cdn\.jornalotempo\.com\.br/videos")):
                details['tem_video'] = True

        # Tags
        tags_container = soup.find('div', class_='tags')
        if tags_container and tags_container.ul:
            tags_list = [tag.get_text(strip=True) for tag in tags_container.ul.find_all('a')]
            details['tags_noticia'] = ", ".join(tags_list) if tags_list else "N/A"

    except Exception as e:
        # If any error occurs, the default "error" values are returned
        print(f"    [Scraper Warning] Erro ao raspar detalhes de {article_url}: {e}")
        pass

    return details


def run_scraper(search_term: str, limit_pages: int = None, limit_articles: int = None, headless: bool = True, status_callback=print):
    """
    Orchestrates the web scraping process for 'O Tempo' news.

    Args:
        search_term (str): The term to search for.
        limit_pages (int, optional): The maximum number of pages to scrape. Defaults to None (all pages).
        limit_articles (int, optional): The maximum number of articles to scrape. Defaults to None (all articles).
        headless (bool, optional): Whether to run the browser in headless mode. Defaults to True.
        status_callback (callable, optional): A function to call with status updates. Defaults to print.

    Returns:
        A list of dictionaries, where each dictionary represents a scraped article.
    """
    driver = _setup_driver(headless)
    all_articles = []
    page_num = 1

    try:
        while True:
            # Check limits before proceeding
            if limit_pages and page_num > limit_pages:
                status_callback(f"Limite de {limit_pages} páginas atingido. Finalizando.")
                break
            if limit_articles and len(all_articles) >= limit_articles:
                status_callback(f"Limite de {limit_articles} notícias atingido. Finalizando.")
                break

            query_string = f"q={quote(search_term)}"
            search_url = f"{URL_BASE}/busca?{query_string}&page={page_num}"
            status_callback(f"\n--- Acessando página de busca {page_num} para '{search_term}' ---")
            driver.get(search_url)

            try:
                # Wait for the main container and at least one item to be visible
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'hits')))
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ais-Hits-item')))
                time.sleep(1) # Extra pause for stability
            except Exception:
                status_callback(f"Não foi possível carregar os resultados da página {page_num} ou não há mais páginas. Finalizando.")
                break

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            article_elements = soup.find_all('li', class_='ais-Hits-item')

            if not article_elements:
                status_callback(f"Nenhuma notícia encontrada na página {page_num}. Finalizando.")
                break

            for i, article_element in enumerate(article_elements):
                if limit_articles and len(all_articles) >= limit_articles:
                    break

                link_tag = article_element.find('a', class_='search-results')
                if not link_tag:
                    continue

                article_url = urljoin(URL_BASE, link_tag['href'])
                title = link_tag.find('h2', class_='search-results__texto--title')
                subtitle = link_tag.find('h3', class_='search-results__texto--subtitle')

                article_summary = {
                    'titulo': title.get_text(strip=True) if title else "N/A",
                    'subtitulo': subtitle.get_text(strip=True) if subtitle else "N/A",
                    'link_noticia': article_url
                }

                status_callback(f"  Coletando detalhes da notícia {i+1}/{len(article_elements)}: {article_summary['titulo']}")
                time.sleep(1.5) # Be respectful to the server

                details = _scrape_article_details(driver, article_url)

                # Combine summary and details
                full_article_data = {**article_summary, **details}
                all_articles.append(full_article_data)

            page_num += 1

    except Exception as e:
        status_callback(f"[Scraper Error] Ocorreu um erro inesperado: {e}")
    finally:
        if driver:
            driver.quit()
        status_callback("\nColeta de dados finalizada.")

    return all_articles
