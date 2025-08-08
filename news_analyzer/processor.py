import locale
import pandas as pd

def _set_portuguese_locale():
    """Tries to set the locale to Portuguese for correct month name parsing."""
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except locale.Error:
            print("Aviso: Não foi possível configurar o locale para pt_BR. Nomes de meses podem não ser analisados corretamente.")

def load_and_clean_data(filepath: str):
    """
    Loads a CSV file into a pandas DataFrame and performs initial cleaning.

    Args:
        filepath (str): The path to the input CSV file.

    Returns:
        A cleaned pandas DataFrame, or None if the file is not found.
    """
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{filepath}'")
        return None

    # Drop rows with missing essential info
    df.dropna(subset=['titulo', 'link_noticia'], inplace=True)

    # Replace known error strings with NaN
    error_strings = [
        "Erro ao coletar data", "Erro", "Erro ao coletar texto",
        "Erro ao coletar imagem", "Erro ao coletar repórter", "Erro ao coletar tags"
    ]
    df.replace(error_strings, pd.NA, inplace=True)

    # Drop columns that are completely empty
    df.dropna(axis=1, how='all', inplace=True)

    return df

def perform_temporal_analysis(df: pd.DataFrame):
    """
    Converts date strings to datetime objects and extracts year and month.

    Args:
        df (pd.DataFrame): The input DataFrame. Must contain a 'data_pura' column.

    Returns:
        The DataFrame with added datetime columns ('data_dt', 'ano_publicacao', etc.).
    """
    if 'data_pura' not in df.columns:
        print("Aviso: Coluna 'data_pura' não encontrada. Pulando análise temporal.")
        return df

    _set_portuguese_locale()

    # Convert 'dd de mes de yyyy' to datetime objects
    df['data_para_dt'] = df['data_pura'].astype(str).str.replace(' de ', ' ', regex=False)
    df['data_dt'] = pd.to_datetime(df['data_para_dt'], format='%d %B %Y', errors='coerce')
    df.drop(columns=['data_para_dt'], inplace=True)

    # Extract year and month, handling potential NaT values
    df['ano_publicacao'] = df['data_dt'].dt.year.astype('Int64')
    df['mes_publicacao'] = df['data_dt'].dt.strftime('%B')
    df['mes_numero'] = df['data_dt'].dt.month.astype('Int64')

    return df

def generate_summary_reports(df: pd.DataFrame):
    """
    Generates monthly and yearly summary reports from the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame after temporal analysis.

    Returns:
        A tuple containing two DataFrames: (monthly_counts, yearly_counts).
    """
    if 'data_dt' not in df.columns:
        print("Aviso: Coluna 'data_dt' não encontrada. Não é possível gerar relatórios.")
        return pd.DataFrame(), pd.DataFrame()

    df_valid_dates = df.dropna(subset=['data_dt'])

    # Yearly report
    yearly_counts = df_valid_dates.groupby('ano_publicacao').size().reset_index(name='total_noticias')
    yearly_counts = yearly_counts.sort_values(by='ano_publicacao')

    # Monthly report
    monthly_counts = df_valid_dates.groupby(['ano_publicacao', 'mes_publicacao', 'mes_numero']).size().reset_index(name='total_noticias')
    monthly_counts = monthly_counts.sort_values(by=['ano_publicacao', 'mes_numero'])

    return monthly_counts, yearly_counts

def save_processed_data(df, monthly_report, yearly_report, output_prefix):
    """
    Saves the main DataFrame and the summary reports to CSV files.

    Args:
        df (pd.DataFrame): The main processed DataFrame.
        monthly_report (pd.DataFrame): The monthly summary report.
        yearly_report (pd.DataFrame): The yearly summary report.
        output_prefix (str): The prefix for the output filenames.
    """
    # Define columns to save for the main analyzed file
    cols_to_save = [
        'titulo', 'subtitulo', 'data_pura', 'horario', 'link_noticia',
        'texto_completo', 'link_imagem_principal', 'tem_video', 'nome_reporter',
        'tags_noticia', 'data_dt', 'ano_publicacao', 'mes_publicacao', 'mes_numero'
    ]
    # Filter for columns that actually exist in the DataFrame
    existing_cols = [col for col in cols_to_save if col in df.columns]

    try:
        # Save main processed data
        main_output_path = f"{output_prefix}_analisadas.csv"
        df[existing_cols].to_csv(main_output_path, index=False, encoding='utf-8')
        print(f"DataFrame principal salvo em: {main_output_path}")

        # Save monthly report
        monthly_output_path = f"{output_prefix}_contagem_mensal.csv"
        monthly_report.to_csv(monthly_output_path, index=False, encoding='utf-8')
        print(f"Relatório mensal salvo em: {monthly_output_path}")

        # Save yearly report
        yearly_output_path = f"{output_prefix}_contagem_anual.csv"
        yearly_report.to_csv(yearly_output_path, index=False, encoding='utf-8')
        print(f"Relatório anual salvo em: {yearly_output_path}")

    except Exception as e:
        print(f"Erro ao salvar os arquivos CSV: {e}")
