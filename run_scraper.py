import argparse
import csv
import re
from news_analyzer.scraper import run_scraper

def save_to_csv(data, search_term):
    """Saves a list of dictionaries to a CSV file."""
    if not data:
        print("Nenhum dado para salvar.")
        return

    # Create a safe filename from the search term
    term_for_filename = re.sub(r'[^\w\s-]', '', search_term).replace(' ', '_').lower()
    csv_file_path = f'noticias_otempo_{term_for_filename}_separado.csv'

    try:
        # Ensure all possible keys are used as fieldnames
        fieldnames = list(data[0].keys())
        for row in data:
            for key in row.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"\nDados salvos com sucesso em '{csv_file_path}'")
    except Exception as e:
        print(f"\nErro ao salvar os dados no arquivo CSV: {e}")

def main():
    """Main function to run the scraper from the command line."""
    parser = argparse.ArgumentParser(
        description="""
        O Tempo Scraper News - Ferramenta para capturar notícias do portal O Tempo.
        Desenvolvido por Humberto Trajano, refatorado por Jules.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "search_term",
        metavar="TERMO_BUSCA",
        type=str,
        help="O termo de busca para a pesquisa. Ex: 'inteligência artificial'"
    )
    parser.add_argument(
        "--pages",
        dest="limit_pages",
        type=int,
        default=None,
        help="Número máximo de páginas de resultados a serem coletadas."
    )
    parser.add_argument(
        "--articles",
        dest="limit_articles",
        type=int,
        default=None,
        help="Número máximo de notícias a serem coletadas."
    )
    parser.add_argument(
        "--show-browser",
        dest="headless",
        action="store_false",
        help="Exibe a janela do navegador durante a coleta. (Padrão: roda em segundo plano)"
    )

    args = parser.parse_args()

    print("************************************")
    print("Iniciando O Tempo Scraper News")
    print(f"Buscando por: '{args.search_term}'")
    if args.limit_pages:
        print(f"Limite de páginas: {args.limit_pages}")
    if args.limit_articles:
        print(f"Limite de notícias: {args.limit_articles}")
    print("************************************")

    # The `print` function is used as a simple status callback
    scraped_data = run_scraper(
        search_term=args.search_term,
        limit_pages=args.limit_pages,
        limit_articles=args.limit_articles,
        headless=args.headless,
        status_callback=print
    )

    if scraped_data:
        save_to_csv(scraped_data, args.search_term)
    else:
        print(f"Nenhuma notícia foi coletada para o termo '{args.search_term}'.")

if __name__ == "__main__":
    main()
