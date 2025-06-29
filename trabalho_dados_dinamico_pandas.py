import pandas as pd
import locale
import re

import matplotlib.pyplot as plt
import platform
try:
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
except Exception as e:
    print(f"Aviso: Não foi possível configurar a fonte para 'DejaVu Sans'. Acentuação em gráficos pode não aparecer. Erro: {e}")
    try:
        if 'Windows' in platform.system():
            plt.rcParams['font.family'] = 'Arial'
            plt.rcParams['font.sans-serif'] = ['Arial']
    except Exception as e_fallback:
        print(f"Aviso: Fallback para Arial também falhou. Gráficos podem ter problemas de acentuação. Erro: {e_fallback}")


def processar_csv_noticias():
    """
    Processa um arquivo CSV de notícias, realiza limpeza de dados,
    converte e analisa a coluna de data para análises temporais (anual e mensal).
    Permite ao usuário especificar o nome do arquivo CSV.
    """
    csv_file_name_input = input("Por favor, digite o NOME COMPLETO do arquivo CSV a ser analisado (ex: noticias_otempo_cafe_com_politica_separado.csv): ")

    csv_file_path = csv_file_name_input

    base_name = csv_file_name_input.rsplit('.', 1)[0]
    output_csv_file_path = f"{base_name}_analisadas.csv"
    
    # Nomes para os arquivos CSV das análises
    output_monthly_count_csv = f"{base_name}_contagem_mensal.csv"
    output_yearly_count_csv = f"{base_name}_contagem_anual.csv"


    print(f"\nTentando ler o arquivo CSV: {csv_file_path}")

    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8')

        print("\nArquivo CSV lido com sucesso!")
        print("\n--- Primeiras 5 linhas do DataFrame (original) ---")
        print(df.head())

        print("\n--- Informações básicas sobre o DataFrame (original) ---")
        df.info()

        # === INÍCIO DA LIMPEZA DE DADOS INCONSISTENTES ===
        print("\n--- Iniciando limpeza de dados inconsistentes ---")

        linhas_antes = len(df)
        df.dropna(subset=['titulo', 'link_noticia'], inplace=True)
        linhas_depois = len(df)
        if linhas_antes > linhas_depois:
            print(f"  Removidas {linhas_antes - linhas_depois} linhas com título ou link ausentes.")

        df.replace("Erro ao coletar data", pd.NA, inplace=True)
        df.replace("Erro", pd.NA, inplace=True)
        df.replace("Erro ao coletar texto", pd.NA, inplace=True)
        df.replace("Erro ao coletar imagem", pd.NA, inplace=True)
        df.replace("Erro ao coletar repórter", pd.NA, inplace=True)
        df.replace("Erro ao coletar tags", pd.NA, inplace=True)
        print("  Strings de erro substituídas por valores nulos (NaN).")

        cols_before_drop_empty = df.shape[1]
        df.dropna(axis=1, how='all', inplace=True)
        cols_after_drop_empty = df.shape[1]
        if cols_before_drop_empty > cols_after_drop_empty:
            print(f"  Removidas {cols_before_drop_empty - cols_after_drop_empty} colunas que estavam completamente vazias.")

        print("--- Limpeza de dados concluída ---")
        print("\n--- Informações do DataFrame após limpeza ---")
        print(df.info())
        # === FIM DA LIMPEZA DE DADOS INCONSISTENTES ===


        # === ANÁLISE TEMPORAL: CONVERSÃO PARA DATETIME E AGRUPAMENTO ===
        print("\n--- Análise Temporal: Convertendo 'data_pura' para datetime ---")
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
            except locale.Error:
                print("Aviso: Não foi possível configurar o local para português. Análises temporais podem ser afetadas.")
                pass

        df['data_para_dt'] = df['data_pura'].astype(str).str.replace(' de ', ' ', regex=False)
        df['data_dt'] = pd.to_datetime(df['data_para_dt'], format='%d %B %Y', errors='coerce')
        df = df.drop(columns=['data_para_dt'])

        df['ano_publicacao'] = df['data_dt'].dt.year.astype('Int64')
        df['mes_publicacao'] = df['data_dt'].dt.strftime('%B')
        df['mes_numero'] = df['data_dt'].dt.month

        print("\n--- Contagem de Notícias por Ano e Mês de Publicação ---")
        contagem_por_ano_mes = df.dropna(subset=['data_dt']).groupby(['ano_publicacao', 'mes_publicacao', 'mes_numero']).size().reset_index(name='total_noticias')

        meses_ordem = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        contagem_por_ano_mes['mes_num'] = contagem_por_ano_mes['mes_publicacao'].apply(lambda x: meses_ordem.index(x.lower()))

        contagem_por_ano_mes_ordenada = contagem_por_ano_mes.sort_values(by=['ano_publicacao', 'mes_num']).drop(columns=['mes_num'])
        print(contagem_por_ano_mes_ordenada)

        # === Contagem de Notícias por Mês no Período Específico (Jul/2023 a Jun/2025) ===
        print("\n--- Contagem de Notícias por Mês (Jul/2023 a Jun/2025) ---")

        df_periodo_filtrado = df.dropna(subset=['data_dt']).copy()

        data_inicio_periodo = pd.to_datetime('2023-07-01')
        data_fim_periodo = pd.to_datetime('2025-06-30')

        df_periodo_filtrado = df_periodo_filtrado[(df_periodo_filtrado['data_dt'] >= data_inicio_periodo) & \
                                                   (df_periodo_filtrado['data_dt'] <= data_fim_periodo)]

        contagem_mensal_periodo = df_periodo_filtrado.groupby(['ano_publicacao', 'mes_publicacao', 'mes_numero']).size().reset_index(name='total_noticias') # Ajustado para agrupar por ano, mes_nome e mes_numero
        contagem_mensal_periodo_final = contagem_mensal_periodo.sort_values(by=['ano_publicacao', 'mes_numero']).drop(columns=['mes_numero'])
        print(contagem_mensal_periodo_final)

        # === NOVO: Salvar Contagem Mensal em CSV ===
        try:
            contagem_mensal_periodo_final.to_csv(output_monthly_count_csv, index=False, encoding='utf-8')
            print(f"  Contagem mensal salva em '{output_monthly_count_csv}'")
        except Exception as e:
            print(f"  Erro ao salvar contagem mensal em CSV: {e}")
        # === FIM DO NOVO ===

        # === Contagem de Notícias por Ano ===
        print("\n--- Contagem de Notícias por Ano de Publicação ---")
        contagem_por_ano = df.dropna(subset=['ano_publicacao']).groupby('ano_publicacao').size().reset_index(name='total_noticias')
        print(contagem_por_ano.sort_values(by='ano_publicacao'))

        # === NOVO: Salvar Contagem Anual em CSV ===
        try:
            contagem_por_ano.to_csv(output_yearly_count_csv, index=False, encoding='utf-8')
            print(f"  Contagem anual salva em '{output_yearly_count_csv}'")
        except Exception as e:
            print(f"  Erro ao salvar contagem anual em CSV: {e}")
        # === FIM DO NOVO ===


        # === SALVAR O DATAFRAME MODIFICADO ===
        print(f"\nSalvando o DataFrame modificado em: {output_csv_file_path}")
        colunas_para_salvar = [
            'titulo', 'subtitulo', 'data_pura', 'horario', 'link_noticia',
            'texto_completo', 'link_imagem_principal', 'tem_video', 'nome_reporter', 'tags_noticia',
            'data_dt', 'ano_publicacao', 'mes_publicacao', 'mes_numero'
        ]
        cols_to_save_exist = [col for col in colunas_para_salvar if col in df.columns]
        df[cols_to_save_exist].to_csv(output_csv_file_path, index=False, encoding='utf-8')
        print("DataFrame salvo com sucesso!")

        # === EXEMPLOS DE ANÁLISE BÁSICA (continuam funcionando) ===
        print("\n--- Primeiras 5 linhas do DataFrame (após todas as análises) ---")
        print(df.head())
        print("\n--- Informações básicas sobre o DataFrame (após todas as análises) ---")
        print(df.info())

        print("\n--- Contagem de notícias por Data (texto) ---")
        contagem_por_data = df['data_pura'].value_counts().reset_index(name='total_noticias')
        contagem_por_data.columns = ['data_publicacao_limpa', 'total_noticias']
        print(contagem_por_data.sort_values(by='data_publicacao_limpa'))

        print("\n--- 5 Notícias mais recentes ---")
        print(df.sort_values(by='data_dt', ascending=False).head()[['titulo', 'data_dt', 'link_noticia']])


    except FileNotFoundError:
        print(f"Erro: O arquivo '{csv_file_path}' não foi encontrado.")
        print("Verifique se o nome digitado está correto e se o arquivo está na mesma pasta do script.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler ou processar o arquivo CSV: {e}")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    processar_csv_noticias()