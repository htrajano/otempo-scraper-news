import pandas as pd
import re
from collections import Counter
from nltk.corpus import stopwords
from nltk.util import ngrams 
import nltk
from wordcloud import WordCloud 
import matplotlib.pyplot as plt 
import matplotlib.font_manager as fm 
import platform 
import csv 

# Configuração para garantir que o Matplotlib use uma fonte que suporte acentuação
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


def encontrar_palavras_mais_usadas():
    """
    Este script encontra as palavras mais usadas, bigrams e trigrams nos títulos,
    subtítulos e texto completo das notícias de um arquivo CSV gerado pela raspagem.
    Também gera nuvens de palavras e gráficos de barras para as tags,
    e salva todos os resultados em um arquivo CSV consolidado.
    """
    csv_file_name_input = input("Por favor, digite o NOME COMPLETO do arquivo CSV a ser analisado (ex: noticias_otempo_cafe_com_politica_completo.csv): ")
    
    csv_file_path = csv_file_name_input 

    print(f"\nTentando ler o arquivo CSV: {csv_file_path}")

    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8')

        print("\nArquivo CSV lido com sucesso!")
        
        # Garante que as stopwords do NLTK foram baixadas.
        try:
            stopwords.words('portuguese')
        except LookupError:
            print("Baixando stopwords do NLTK. Isso só acontecerá uma vez.")
            nltk.download('stopwords')
            
        stop_words_pt = set(stopwords.words('portuguese'))
        # === AQUI ESTÃO AS NOVAS STOPWORDS ADICIONADAS ===
        stop_words_pt.update(['tempo', 'de acordo', 'noticia', 'notícias', 'diz', 'vai', 'pode', 'anos', 'um', 'uma', 'dois', 'duas', 'ser', 'ter', 'fazer', 'são', 'deve', 'feira', 'conforme', 'segundo', 'em']) # Adicionado 'em' também, que é muito comum.
        # =================================================

        # Função auxiliar para limpar e tokenizar o texto
        def clean_and_tokenize(text):
            clean_text = re.sub(r'[^a-zA-ZáéíóúãõâêôàçüÁÉÍÓÚÃÕÂÊÔÀÇÜ\s-]', '', text).lower()
            words = clean_text.split()
            filtered_words = [word for word in words if word not in stop_words_pt and len(word) > 2]
            return filtered_words

        # Função auxiliar para processar e contar N-grams de uma coluna
        def processar_e_contar_ngrams(column_series, n=1, top_n=50, title_prefix=""):
            all_ngrams = []
            for text in column_series.dropna(): 
                words = clean_and_tokenize(text)
                current_ngrams = list(ngrams(words, n))
                all_ngrams.extend([' '.join(gram) for gram in current_ngrams])
            
            ngram_counts = Counter(all_ngrams)
            
            # Print no terminal
            print(f"\n--- Analisando os {top_n} {title_prefix} ({n}-grams) ---")
            print("Termo           | Frequência")
            print("---------------------------------")
            for term, count in ngram_counts.most_common(top_n):
                print(f"{term:<17} | {count}")
            print("---------------------------------\n")
            return ngram_counts.most_common(top_n) 

        # Função auxiliar para gerar e exibir Nuvem de Palavras
        def gerar_e_exibir_nuvem(text_series, title, stop_words):
            full_text = ' '.join(text_series.fillna('').astype(str).tolist())
            
            if not full_text.strip(): 
                print(f"Não há texto suficiente na coluna '{title}' para gerar a nuvem de palavras. Pulando.")
                return 

            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white', 
                stopwords=stop_words, 
                min_font_size=10, 
                max_words=100, 
                collocations=False 
            ).generate(full_text)

            plt.figure(figsize=(10, 5)) 
            plt.imshow(wordcloud, interpolation='bilinear') 
            plt.axis('off') 
            plt.title(f"Nuvem de Palavras: {title}") 
            plt.show() 

        # Função auxiliar para gerar e exibir Gráfico de Barras (para tags)
        def gerar_e_exibir_grafico_barras(data, title, x_label, y_label, top_n=20):
            if not data:
                print(f"Não há dados para gerar o gráfico de barras para '{title}'. Pulando.")
                return

            labels = [item[0] for item in data[:top_n]]
            counts = [item[1] for item in data[:top_n]]

            plt.figure(figsize=(12, 6))
            plt.barh(labels[::-1], counts[::-1], color='skyblue') 
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title)
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout() 
            plt.show()

        # === LISTAS PARA ARMAZENAR RESULTADOS PARA SALVAMENTO ===
        resultados_frequencia = []

        # === INÍCIO DAS ANÁLISES DE TEXTO E N-GRAMS ===
        print("\n--- INÍCIO DA ANÁLISE DE PALAVRAS E N-GRAMS ---")
        
        top_words_titulo = processar_e_contar_ngrams(df['titulo'], n=1, top_n=50, title_prefix="Palavras nos Títulos")
        resultados_frequencia.append({'Tipo': 'Palavras - Títulos', 'Termos': top_words_titulo})
        top_bigrams_titulo = processar_e_contar_ngrams(df['titulo'], n=2, top_n=50, title_prefix="Bigrams nos Títulos")
        resultados_frequencia.append({'Tipo': 'Bigrams - Títulos', 'Termos': top_bigrams_titulo})
        top_trigrams_titulo = processar_e_contar_ngrams(df['titulo'], n=3, top_n=50, title_prefix="Trigrams nos Títulos")
        resultados_frequencia.append({'Tipo': 'Trigrams - Títulos', 'Termos': top_trigrams_titulo})
        
        if 'subtitulo' in df.columns and not df['subtitulo'].isnull().all():
            top_words_subtitulo = processar_e_contar_ngrams(df['subtitulo'], n=1, top_n=50, title_prefix="Palavras nos Subtítulos")
            resultados_frequencia.append({'Tipo': 'Palavras - Subtítulos', 'Termos': top_words_subtitulo})
            top_bigrams_subtitulo = processar_e_contar_ngrams(df['subtitulo'], n=2, top_n=50, title_prefix="Bigrams nos Subtítulos")
            resultados_frequencia.append({'Tipo': 'Bigrams - Subtítulos', 'Termos': top_bigrams_subtitulo})
            top_trigrams_subtitulo = processar_e_contar_ngrams(df['subtitulo'], n=3, top_n=50, title_prefix="Trigrams nos Subtítulos")
            resultados_frequencia.append({'Tipo': 'Trigrams - Subtítulos', 'Termos': top_trigrams_subtitulo})
        else:
            print("Coluna 'subtitulo' não encontrada ou vazia no CSV. Pulando análise de subtítulos.\n")

        if 'texto_completo' in df.columns and not df['texto_completo'].isnull().all():
            top_words_texto = processar_e_contar_ngrams(df['texto_completo'], n=1, top_n=50, title_prefix="Palavras no Texto Completo")
            resultados_frequencia.append({'Tipo': 'Palavras - Texto Completo', 'Termos': top_words_texto})
            top_bigrams_texto = processar_e_contar_ngrams(df['texto_completo'], n=2, top_n=50, title_prefix="Bigrams no Texto Completo")
            resultados_frequencia.append({'Tipo': 'Bigrams - Texto Completo', 'Termos': top_bigrams_texto})
            top_trigrams_texto = processar_e_contar_ngrams(df['texto_completo'], n=3, top_n=50, title_prefix="Trigrams no Texto Completo")
            resultados_frequencia.append({'Tipo': 'Trigrams - Texto Completo', 'Termos': top_trigrams_texto})
        else:
            print("Coluna 'texto_completo' não encontrada ou vazia no CSV. Pulando análise de texto completo.\n")
        
        print("\n--- FIM DA ANÁLISE DE PALAVRAS E N-GRAMS ---\n")

        # === INÍCIO DA ANÁLISE DE TAGS E GERAÇÃO DE GRÁFICOS ===
        print("--- INÍCIO DA ANÁLISE DE TAGS ---")
        top_tags_results = [] # Para armazenar as tags mais comuns para salvamento
        if 'tags_noticia' in df.columns and not df['tags_noticia'].isnull().all():
            all_tags = []
            for tags_str in df['tags_noticia'].dropna():
                tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                all_tags.extend(tags_list)
            
            if all_tags: 
                tag_counts = Counter(all_tags)
                top_tags_results = tag_counts.most_common(50) # Top 50 tags para lista e salvamento

                # Exibir lista das tags mais frequentes no terminal
                print("\n--- 50 Tags Mais Frequentes (Lista) ---")
                print("Tag                 | Frequência")
                print("---------------------------------")
                for tag, count in top_tags_results:
                    print(f"{tag:<19} | {count}")
                print("---------------------------------\n")

                # Gerar gráfico de barras para as tags (top 20 para visualização)
                gerar_e_exibir_grafico_barras(top_tags_results, "20 Tags Mais Frequentes nas Notícias", "Frequência", "Tag", top_n=20)

                # Gerar Nuvem de Palavras para Tags (top 100 para visualização)
                gerar_e_exibir_nuvem(pd.Series(all_tags), "Tags das Notícias (Nuvem)", stop_words_pt)
            else:
                print("Coluna 'tags_noticia' encontrada, mas sem tags válidas para análise.\n")
        else:
            print("Coluna 'tags_noticia' não encontrada ou vazia no CSV. Pulando análise de tags.\n")
        print("\n--- FIM DA ANÁLISE DE TAGS ---\n")

        # === GERAÇÃO DE NUVEM DE PALAVRAS (para Títulos, Subtítulos e Texto Completo) ===
        print("--- INÍCIO DA GERAÇÃO DE NUVEM DE PALAVRAS (geral) ---")
        gerar_e_exibir_nuvem(df['titulo'], "Títulos das Notícias", stop_words_pt)

        if 'subtitulo' in df.columns and not df['subtitulo'].isnull().all():
            gerar_e_exibir_nuvem(df['subtitulo'], "Subtítulos das Notícias", stop_words_pt)
        
        if 'texto_completo' in df.columns and not df['texto_completo'].isnull().all():
            gerar_e_exibir_nuvem(df['texto_completo'], "Texto Completo das Notícias", stop_words_pt)
        print("\n--- FIM DA GERAÇÃO DE NUVEM DE PALAVRAS (geral) ---\n")

        # === SALVAR TODOS OS RESULTADOS DE FREQUÊNCIA EM UM CSV CONSOLIDADO ===
        output_base_name = csv_file_path.rsplit('.', 1)[0]
        results_csv_path = f'{output_base_name}_analise_textual.csv'
        
        consolidated_data = []
        # Adiciona os resultados de N-grams
        for res_type in resultados_frequencia:
            for term, count in res_type['Termos']:
                consolidated_data.append({'Tipo de Análise': res_type['Tipo'], 'Termo': term, 'Frequência': count})
        
        # Adiciona os resultados de Tags
        for tag, count in top_tags_results: # Usar top_tags_results aqui
            consolidated_data.append({'Tipo de Análise': 'Tags Mais Frequentes', 'Termo': tag, 'Frequência': count})

        if consolidated_data:
            print(f"\nSalvando resultados da análise textual em: {results_csv_path}")
            with open(results_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames_results = ['Tipo de Análise', 'Termo', 'Frequência']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames_results)
                writer.writeheader()
                writer.writerows(consolidated_data)
            print("Resultados da análise textual salvos com sucesso!")
        else:
            print("Nenhum resultado de análise textual para salvar.")
        

    except FileNotFoundError:
        print(f"Erro: O arquivo '{csv_file_path}' não foi encontrado.")
        print("Verifique se o nome digitado está correto e se o arquivo está na mesma pasta do script.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler ou processar o arquivo CSV: {e}")

if __name__ == "__main__":
    encontrar_palavras_mais_usadas()