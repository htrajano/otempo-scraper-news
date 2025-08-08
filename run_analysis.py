import argparse
import pandas as pd
import os
import csv

# Import the refactored logic from the news_analyzer library
from news_analyzer import processor
from news_analyzer import text_analyzer

def save_frequency_results(results_dict, output_path):
    """Saves a dictionary of frequency analysis results to a single CSV."""
    consolidated_data = []
    for analysis_type, data in results_dict.items():
        for term, frequency in data:
            consolidated_data.append({
                'Tipo de Análise': analysis_type,
                'Termo': term,
                'Frequência': frequency
            })

    if not consolidated_data:
        print("Nenhum dado de frequência para salvar.")
        return

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['Tipo de Análise', 'Termo', 'Frequência']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(consolidated_data)
        print(f"Resultados da análise de frequência salvos em: {output_path}")
    except Exception as e:
        print(f"Erro ao salvar o CSV de análise de frequência: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="""
        Executa o pipeline completo de processamento e análise de texto em um arquivo de notícias CSV.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_file",
        metavar="ARQUIVO_CSV",
        type=str,
        help="Caminho para o arquivo CSV gerado pelo scraper."
    )
    args = parser.parse_args()

    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"Erro: O arquivo de entrada '{input_path}' não foi encontrado.")
        return

    # Create an output directory based on the input filename
    base_name = os.path.basename(input_path).rsplit('.', 1)[0]
    output_dir = f"analise_{base_name}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Todos os resultados serão salvos no diretório: '{output_dir}/'")

    output_prefix = os.path.join(output_dir, base_name)

    # --- 1. Processing and Temporal Analysis ---
    print("\n--- Iniciando Etapa 1: Processamento e Análise Temporal ---")
    df = processor.load_and_clean_data(input_path)
    if df is None:
        return # Stop if file could not be loaded

    df = processor.perform_temporal_analysis(df)
    monthly_report, yearly_report = processor.generate_summary_reports(df)
    processor.save_processed_data(df, monthly_report, yearly_report, output_prefix)
    print("--- Etapa 1 Concluída ---")

    # --- 2. Text Analysis ---
    print("\n--- Iniciando Etapa 2: Análise de Texto ---")

    # Check if text columns exist before proceeding
    text_columns = {
        'titulo': 'Títulos',
        'subtitulo': 'Subtítulos',
        'texto_completo': 'Texto Completo'
    }

    all_freq_results = {}

    # N-gram analysis
    for col, name in text_columns.items():
        if col in df.columns and not df[col].isnull().all():
            print(f"\nAnalisando N-grams para: {name}")
            all_freq_results[f'Palavras - {name}'] = text_analyzer.get_ngram_frequency(df[col], n=1)
            all_freq_results[f'Bigrams - {name}'] = text_analyzer.get_ngram_frequency(df[col], n=2)
            all_freq_results[f'Trigrams - {name}'] = text_analyzer.get_ngram_frequency(df[col], n=3)

    # Tag analysis
    if 'tags_noticia' in df.columns and not df['tags_noticia'].isnull().all():
        print("\nAnalisando Tags...")
        tag_freq = text_analyzer.get_tag_frequency(df['tags_noticia'])
        all_freq_results['Tags Mais Frequentes'] = tag_freq
        text_analyzer.create_barchart(
            tag_freq,
            title="Top 20 Tags Mais Frequentes",
            output_path=f"{output_prefix}_grafico_tags.png"
        )

    # Save all frequency results to a single CSV
    save_frequency_results(all_freq_results, f"{output_prefix}_analise_frequencia.csv")

    # Word cloud generation
    print("\nGerando Nuvens de Palavras...")
    for col, name in text_columns.items():
        if col in df.columns and not df[col].isnull().all():
            text_analyzer.create_wordcloud(
                df[col],
                output_path=f"{output_prefix}_nuvem_{col}.png"
            )

    print("--- Etapa 2 Concluída ---")
    print("\nAnálise completa!")

if __name__ == "__main__":
    main()
