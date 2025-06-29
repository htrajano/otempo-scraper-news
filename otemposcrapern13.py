import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from urllib.parse import quote, urljoin
from webdriver_manager.firefox import GeckoDriverManager

"""
Documentação do Script: otemposcrapern.py

Propósito:
----------
Este programa, "O Tempo Scraper News", é uma ferramenta de pesquisa científica desenvolvida em Python
com o objetivo de capturar notícias do portal de jornalismo O Tempo (otempo.com.br).
Ele oferece uma interface amigável para o usuário, permitindo buscas dinâmicas e controle sobre
a quantidade de dados a serem raspados.

Recursos Principais:
-   **Interação com o Usuário:** Solicita o termo de busca e as opções de quantidade de captura.
-   **Busca Dinâmica:** Realiza pesquisas por qualquer termo especificado pelo usuário no site O Tempo.
-   **Controle de Captura:** Permite ao usuário escolher entre capturar todas as notícias,
    um número específico de páginas ou um número específico de notícias (as mais recentes).
-   **Paginação Robusta:** Navega por todas as páginas de resultados da busca utilizando
    a estrutura de URL do site (parâmetro 'page') e esperas inteligentes para lidar com
    conteúdo carregado dinamicamente (AJAX).
-   **Extração Detalhada:** Para cada notícia, extrai os seguintes campos:
    -   `titulo`: Título da notícia (obtido da página de busca).
    -   `subtitulo`: Subtítulo/resumo da notícia (obtido da página de busca).
    -   `data_pura`: Data de publicação da notícia (ex: "11 de junho de 2025").
    -   `horario`: Horário de publicação da notícia (ex: "18:05").
    -   `nome_reporter`: Nome do(s) repórter(es) ou autor(es) da notícia.
    -   `link_noticia`: URL completo da notícia individual.
    -   `texto_completo`: Conteúdo textual integral da notícia (todos os parágrafos).
    -   `link_imagem_principal`: URL da imagem principal da notícia.
    -   `tem_video`: Booleano (True/False) indicando a presença de vídeo na notícia.
    -   `tags_noticia`: Lista de tags associadas à notícia (separadas por vírgulas).
-   **Salvamento em CSV:** Todos os dados raspados são automaticamente exportados
    para um arquivo CSV com um nome baseado no termo de busca (ex: `noticias_otempo_meu_termo_separado.csv`),
    pronto para análise.
-   **Feedback Visual:** Exibe mensagens de progresso no terminal e, opcionalmente,
    mostra o navegador Firefox em ação.

Informações de Autoria:
-----------------------
Desenvolvido por **Humberto Trajano - @betotgm**
Como parte de pesquisa de Mestrado em Comunicação na Universidade Federal de Ouro Preto (Ufop), 
sob orientação da professora Luana Viana, financiada com bolsa da instituição.
O código deste software foi escrito com auxílio do Gemini.
Mariana, 2025.

Pré-requisitos para Instalação:
------------------------------
Para executar este script, você precisa ter o Python instalado (versão 3.8 ou superior recomendada)
e as seguintes bibliotecas Python instaladas. Além disso, é necessário ter o navegador
Mozilla Firefox instalado.

1.  **Python:**
    * Verifique sua versão: Abra o **Windows Terminal (PowerShell)** e digite `python --version`.
    * Instalação: Baixe e instale-o do site oficial [python.org](https://www.python.org/).
        **Importante:** Durante a instalação, **MARQUE a opção "Add Python.exe to PATH"**.
2.  **Bibliotecas Python:**
    * Abra seu **Windows Terminal (PowerShell)**.
    * Navegue até a pasta onde você guardará o projeto 
    * Instale as bibliotecas digitando os seguintes comandos (um por um, pressionando Enter após cada um):
        ```powerspowershell
        pip install requests beautifulsoup4 selenium webdriver-manager
        ```
3.  **Navegador Mozilla Firefox:**
    * Certifique-se de que o Firefox está instalado em seu sistema: [mozilla.org/firefox](https://www.mozilla.org/pt-BR/firefox/new/).
    * O `webdriver-manager` (instalado acima) irá baixar e gerenciar o `GeckoDriver` (o driver do Firefox) automaticamente, então você não precisa baixá-lo manualmente.

Como Usar o Programa:
---------------------
1.  **Crie a Pasta do Projeto:** Se ainda não o fez, crie uma pasta para organizar seus arquivos.
2.  **Salve o Script Principal:**
    * Copie **todo o código** deste script (`otemposcrapern.py`) e cole-o em um novo arquivo no **VS Code**.
    * Salve este arquivo como **`otemposcrapern.py`** dentro da sua pasta do projeto.
3.  **Modo de Visualização (Opcional):**
    * Por padrão, o navegador Firefox abrirá visivelmente. Se você preferir que ele rode em segundo plano (sem interface gráfica, o que é mais rápido para grandes volumes de dados), edite o arquivo `otemposcrapern.py` no VS Code.
    * **Descomente** (remova o `#`) da linha:
        ```python
        # options.add_argument('--headless')
        ```
    * Salve o arquivo.
4.  **Inicie o Programa:**
    * Abra seu **Windows Terminal (PowerShell)**.
    * Navegue até a sua pasta do projeto:
        ```powershell
              ```
    * Inicie o programa digitando:
        ```powershell
        python otemposcrapern.py
        ```
5.  **Siga as Instruções no Terminal:**
    * O programa começará com uma mensagem de boas-vindas.
    * Ele pedirá para você **digitar o termo de busca** (ex: `Amazônia`, `Poze do Rodo`, `eleições`, `economia`). Digite o termo e pressione **Enter**.
    * Em seguida, ele fará uma pesquisa inicial e informará o número total de notícias e páginas encontradas para o seu termo.
    * Você será questionado sobre a quantidade de dados a capturar:
        ```
        (P) se você quer coletar por número de páginas
        (N) se deseja indicar o número de notícias
        (T) se você deseja capturar todas
        P, N ou T?:
        ```
        * Digite `P`, `N` ou `T` e siga as instruções adicionais (número de páginas ou notícias).
    * Após sua escolha, o programa confirmará: `Obrigado! Vamos iniciar a coleta.`
    * A janela do Firefox (se não estiver em modo headless) se abrirá e você verá a raspagem acontecendo.
    * **Conclusão:** Ao final, uma mensagem de sucesso será exibida no terminal, informando o nome do arquivo CSV gerado (ex: `noticias_otempo_SEU_TERMO_separado.csv`) e sua localização na pasta do projeto.

Observações Importantes:
------------------------
-   **Dependência do Layout do Site:** Este script é altamente dependente da estrutura HTML (classes CSS e IDs) do site `otempo.com.br`. Se o site mudar seu layout (o que pode acontecer frequentemente), as classes usadas no script precisarão ser atualizadas. Mensagens de erro no terminal (como `NoSuchElementException` ou `TimeoutException`) ajudarão a identificar esses problemas.
-   **Velocidade da Raspagem:** A velocidade de raspagem é controlada por pequenas pausas (`time.sleep`) para evitar sobrecarregar o site e reduzir o risco de bloqueio. Para grandes volumes de dados (muitas páginas/notícias), a execução pode levar várias horas.
-   **Tratamento de Erros:** O script inclui blocos `try-except` para lidar com erros comuns (como elementos não encontrados ou problemas de rede), imprimindo mensagens no terminal e, em caso de erros na paginação ou gerais, mantendo o navegador aberto por 5 minutos para depuração manual.

"""


def raspar_noticias_otempo(termo_busca):
    """
    Raspa informações do site O Tempo para um termo de busca específico,
    com opções de quantidade de raspagem (todas, por número de páginas ou por número de notícias).
    Extrai título, subtítulo, data de publicação (separada), link, texto completo, link da imagem,
    detecção de vídeo, nome do repórter e as tags da notícia.
    Implementa uma lógica de paginação robusta e otimizada por URL, iterando pelas páginas com índice base 1.
    """
    url_base = "https://www.otempo.com.br"
    termo_busca_codificado = quote(termo_busca)
    query_string = f"q={termo_busca_codificado}"
    
    lista_noticias = [] 
    
    # === AGORA AQUI: pagina_algolia_index e pagina_log_display JÁ ESTÃO NO ESCOPO CORRETO ===
    # Eles serão inicializados aqui e incrementados no final do loop.
    pagina_algolia_index = 1 # O parâmetro 'page' no URL do O Tempo para a primeira página é 1
    pagina_log_display = 1   # Para exibir no terminal como 'Página 1', 'Página 2', etc.
    # ======================================================================================

    # Variáveis para controle de quantidade
    total_paginas_encontradas = 0
    total_noticias_estimadas = 0
    limite_paginas_usuario = None
    limite_noticias_usuario = None
    driver = None

    try:
        firefox_driver_path = GeckoDriverManager().install()
        service = Service(executable_path=firefox_driver_path)
        options = webdriver.FirefoxOptions()
        # Mantenha esta linha COMENTADA para ver o navegador em ação!
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        driver = webdriver.Firefox(service=service, options=options)
        
        while True: # Loop para navegar por todas as páginas de busca
            # Inicializa a variável para cada nova página
            noticias_processadas_nesta_pagina = 0 

            # Constrói o URL da página atual da busca
            if pagina_algolia_index == 1: # Para a primeira página
                current_search_url = f"{url_base}/busca?{query_string}"
            else: # Para páginas subsequentes, use o parâmetro 'page'
                current_search_url = f"{url_base}/busca?{query_string}&page={pagina_algolia_index}"

            print(f"\n--- Acessando página de busca {pagina_log_display} para '{termo_busca}': {current_search_url} ---")
            driver.get(current_search_url) 

            # === ESPERAS ROBUSTAS PARA GARANTIR O CARREGAMENTO DA PÁGINA DE BUSCA ATUAL ===
            try:
                # 1. Espera que o contêiner principal de hits seja visível
                WebDriverWait(driver, 45).until(
                    EC.visibility_of_element_located((By.ID, 'hits'))
                )
                
                # 2. Espera que pelo menos UM elemento de notícia esteja visível.
                WebDriverWait(driver, 15).until( 
                    EC.visibility_of_element_located((By.CLASS_NAME, 'ais-Hits-item'))
                )
                
                # 3. Espera que o link da página ATUAL no paginador se torne 'active'.
                paginator_data_page_index = pagina_algolia_index - 1 # Algolia index é 0-based
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"a.pagination__link.active[data-page='{paginator_data_page_index}']"))
                )
                
                time.sleep(2) # Pausa final para garantir a estabilidade do DOM após todas as esperas
                print("Elementos de notícia detectados e visíveis na página de busca.")
            except Exception as e:
                print(f"Erro ao carregar elementos da página de busca {pagina_log_display} para '{termo_busca}'. O site pode ter mudado ou não há mais resultados visíveis.")
                print(f"Detalhes do erro na espera: {e}")
                print("\n**ATENÇÃO:** Página de busca não carregou como esperado. Navegador permanecerá aberto para INSPEÇÃO MANUAL.")
                print("Por favor, verifique se há pop-ups, se a página carregou corretamente ou se as classes HTML mudaram.")
                time.sleep(300) 
                break 

            # === OBTER INFORMAÇÕES TOTAIS E PERGUNTAR AO USUÁRIO (SOMENTE NA PRIMEIRA PÁGINA) ===
            # Este bloco só executa para pagina_algolia_index == 1 (primeira página real do site)
            if pagina_algolia_index == 1:
                page_source_initial = driver.page_source
                soup_initial = BeautifulSoup(page_source_initial, 'html.parser')
                
                pagination_info_div = soup_initial.find('div', class_='pagination__info')
                if pagination_info_div:
                    info_text = pagination_info_div.get_text(strip=True)
                    match = re.search(r'Página \d+ de (\d+)', info_text)
                    if match:
                        total_paginas_encontradas = int(match.group(1))
                        total_noticias_estimadas = total_paginas_encontradas * 8 # Assumimos 8 notícias por página
                        
                        print(f"\nForam encontradas aproximadamente {total_noticias_estimadas} notícias em {total_paginas_encontradas} páginas com este termo.")
                        print("\nAgora digite:")
                        print("(P) se você quer coletar por número de páginas")  
                        print("(N) se deseja indicar o número de notícias ")
                        print("(T) se você deseja capturar todas")
                        
                        while True:
                            escolha = input("P, N ou T?: ").upper().strip()
                            if escolha == 'P':
                                try:
                                    num_paginas = int(input(f"Digite o número de páginas (1 a {total_paginas_encontradas}): "))
                                    if 1 <= num_paginas <= total_paginas_encontradas:
                                        limite_paginas_usuario = num_paginas
                                        break
                                    else:
                                        print("Número de páginas inválido. Tente novamente.")
                                except ValueError:
                                    print("Entrada inválida. Digite um número.")
                            elif escolha == 'N':
                                try:
                                    num_noticias = int(input(f"Digite o número de notícias (1 a {total_noticias_estimadas}): "))
                                    if 1 <= num_noticias <= total_noticias_estimadas:
                                        limite_noticias_usuario = num_noticias
                                        break
                                    else:
                                        print("Número de notícias inválido. Tente novamente.")
                                except ValueError:
                                    print("Entrada inválida. Digite um número.")
                            elif escolha == 'T':
                                print("Capturando todas as notícias.")
                                break
                            else:
                                print("Opção inválida. Digite 'P', 'N' ou 'T'.")
                    else:
                        print("Não foi possível determinar o número total de páginas/notícias. Prosseguindo com todas as páginas.")
                else:
                    print("Informação de paginação não encontrada. Prosseguindo com todas as páginas.")
                
                print("\nObrigado! Vamos iniciar a coleta.")
                time.sleep(2) 
            # === FIM DA SEÇÃO DE OBTENÇÃO DE INFORMAÇÕES TOTAIS ===

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            noticias_elements = soup.find_all('li', class_='ais-Hits-item')

            if not noticias_elements:
                print(f"Nenhuma notícia encontrada na página de busca {pagina_log_display} para '{termo_busca}' com as classes atuais. Finalizando raspagem.")
                break # Se não encontrar notícias, é o fim dos resultados

            for i, noticia_element in enumerate(noticias_elements):
                if limite_noticias_usuario is not None and len(lista_noticias) >= limite_noticias_usuario:
                    print(f"Limite total de {limite_noticias_usuario} notícias atingido. Finalizando raspagem.")
                    break 
                
                titulo = None
                subtitulo = None
                data_publicacao_completa = None 
                data_pura = None 
                horario = None 
                link_noticia = None
                texto_completo = None 
                link_imagem_principal = None 
                tem_video = False 
                nome_reporter = None 
                tags_noticia_str = None 

                link_tag = noticia_element.find('a', class_='search-results')
                if link_tag:
                    link_noticia_rel = link_tag['href']
                    link_noticia = urljoin(url_base, link_noticia_rel) 

                    titulo_tag = link_tag.find('h2', class_='search-results__texto--title')
                    if titulo_tag:
                        titulo = titulo_tag.get_text(separator=' ', strip=True)

                    subtitulo_tag = link_tag.find('h3', class_='search-results__texto--subtitle')
                    if subtitulo_tag:
                        subtitulo = subtitulo_tag.get_text(separator=' ', strip=True)

                if titulo and link_noticia:
                    print(f"  Acessando notícia {i+1} da página {pagina_log_display} para detalhes: {link_noticia}")
                    time.sleep(1.5) 
                    try:
                        driver.get(link_noticia)
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'cp023-assinatura-do-artigo')) 
                        )
                        
                        noticia_soup = BeautifulSoup(driver.page_source, 'html.parser')

                        author_info_div = noticia_soup.find('div', class_='cmp__author-info')
                        if author_info_div:
                            author_name_span = author_info_div.find('span', class_='cmp__author-name')
                            if author_name_span:
                                inner_name_span = author_name_span.find('span') 
                                if inner_name_span:
                                    nome_reporter = inner_name_span.get_text(strip=True)
                                else:
                                    author_link = author_name_span.find('a')
                                    if author_link:
                                        nome_reporter = author_link.get_text(strip=True)
                                    else:
                                        nome_reporter = author_name_span.get_text(strip=True)

                                nome_reporter = re.sub(r'^(Por|Redação)\s*', '', nome_reporter, flags=re.IGNORECASE).strip()
                                nome_reporter = ' '.join(nome_reporter.split())
                                
                        publication_span = noticia_soup.find('span', class_='cmp__author-publication')
                        if publication_span:
                            date_value_span = publication_span.find('span')
                            if date_value_span:
                                data_publicacao_completa = date_value_span.get_text(strip=True)
                                data_publicacao_completa = data_publicacao_completa.split(' - ')[0].strip()
                                
                                if '|' in data_publicacao_completa:
                                    partes = data_publicacao_completa.split('|')
                                    data_pura = partes[0].strip()
                                    horario = partes[1].strip()
                                else: 
                                    data_pura = data_publicacao_completa
                                    horario = "N/A" 
                        
                        texto_principal_div = noticia_soup.find('div', class_='read-controller materia__tts article-whole article-body') 
                        if texto_principal_div:
                            paragrafos = texto_principal_div.find_all('p')
                            texto_completo = '\n'.join([p.get_text(strip=True) for p in paragrafos if p.get_text(strip=True)])
                            
                        gallery_container = noticia_soup.find('div', class_='gallery__container gallery_highlight')
                        if gallery_container:
                            img_tag_principal = gallery_container.find('img', class_='gallery__image')
                            if img_tag_principal and 'src' in img_tag_principal.attrs:
                                link_imagem_principal = img_tag_principal['src']
                                if not link_imagem_principal.startswith('http'):
                                    link_imagem_principal = urljoin(url_base, link_imagem_principal)

                        video_iframe = noticia_soup.find('iframe', class_='c-video__frame') 
                        video_tag = noticia_soup.find('video')
                        
                        iframes_no_corpo = noticia_soup.find('div', class_='c-news-body')
                        if iframes_no_corpo:
                            for iframe in iframes_no_corpo.find_all('iframe'):
                                src = iframe.get('src', '')
                                if 'https://www.youtube.com/embed/G8jXv_yjVVI?si=A-jPxoZqLkP8I1Ry' in src or 'vimeo.com' in src or 'cdn.jornalotempo.com.br/videos' in src:
                                    tem_video = True
                                    break
                        if video_iframe or video_tag: 
                            tem_video = True
                        
                        tags_div_container = noticia_soup.find('div', class_='tags')
                        tags_list = [] 
                        if tags_div_container:
                            ul_tagbox = tags_div_container.find('ul', class_='cmp__tagbox')
                            if ul_tagbox:
                                tags_a_elements = ul_tagbox.find_all('a', class_='label__tag')
                                for tag_a in tags_a_elements:
                                    tags_list.append(tag_a.get_text(strip=True))
                        tags_noticia_str = ", ".join(tags_list) if tags_list else "N/A"

                    except Exception as e_noticia:
                        print(f"    Erro ao acessar ou raspar detalhes da notícia {link_noticia}: {e_noticia}")
                        data_publicacao_completa = "Erro ao coletar data" 
                        data_pura = "Erro ao coletar data" 
                        horario = "Erro" 
                        texto_completo = "Erro ao coletar texto"
                        link_imagem_principal = "Erro ao coletar imagem"
                        tem_video = False 
                        nome_reporter = "Erro ao coletar repórter" 
                        tags_noticia_str = "Erro ao coletar tags" 

                    lista_noticias.append({
                        'titulo': titulo,
                        'subtitulo': subtitulo,
                        'data_pura': data_pura, 
                        'horario': horario, 
                        'link_noticia': link_noticia,
                        'texto_completo': texto_completo, 
                        'link_imagem_principal': link_imagem_principal, 
                        'tem_video': tem_video,
                        'nome_reporter': nome_reporter,
                        'tags_noticia': tags_noticia_str 
                    })
                    time.sleep(0.5) 
                    noticias_processadas_nesta_pagina += 1

            if limite_noticias_usuario is not None and len(lista_noticias) >= limite_noticias_usuario:
                break 

            # --- Lógica para verificar a próxima página ---
            if limite_paginas_usuario is not None and pagina_log_display >= limite_paginas_usuario:
                break

            # === AGORA: Avança os índices para a PRÓXIMA ITERAÇÃO DO LOOP ===
            # E assume que a próxima iteração do loop 'while True' vai navegar para a nova URL.
            
            pagina_algolia_index += 1
            pagina_log_display += 1

            # A condição para quebrar o loop (além dos limites de usuário)
            # é se a próxima página não retornar nenhum 'ais-Hits-item' (notícias).
            # Isso será verificado no topo do loop 'while True' na próxima iteração.
            # Se não houver mais notícias na próxima página, as esperas no topo do loop
            # para #hits e .ais_Hits-item falharão, e o loop será interrompido.
            
    except Exception as e:
        print(f"Ocorreu um erro geral no Selenium ou na raspagem: {e}")
        print("\n**ATENÇÃO:** Erro geral. Navegador permanecerá aberto para inspeção.")
        time.sleep(300) 
    finally:
        if driver:
            driver.quit()

    return lista_noticias 

# Exemplo de uso:
if __name__ == "__main__":
    print("**********************************************************************************************************************")
    print("**********************************************************************************************************************")
    print("Olá, tudo bem?")
    print("Bem-vindo ao O Tempo Scraper News!")
    print("Um programa voltado a pesquisas científicas que tem o objetivo de capturar notícias do portal de jornalismo O Tempo.")
    print("Desenvolvido por Humberto Trajano - @betotgm - como parte de pesquisa de Mestrado em Comunicação na Universidade Federal de Ouro Preto (Ufop), sob orientação da professora Luana Viana, financiada com bolsa da instituição.")
    print("O código deste software foi escrito com auxílio do Gemini.") 
    print("Mariana, 2025")
    print("**********************************************************************************************************************")
    print("**********************************************************************************************************************")
    time.sleep(3) 
    
    print("\nVamos começar os trabalhos!") 
    termo_digitado = input("Digite o termo de busca para pesquisa (ex: Pão de queijo, Galo, Clube da Esquina, eleições, economia, política, música, poesia): ")
    print("Faremos a pesquisa no portal e retornaremos o resultado. ")
    
    noticias_raspadas = raspar_noticias_otempo(termo_digitado) 

    if noticias_raspadas: 
        print(f"\n--- {len(noticias_raspadas)} Notícias encontradas no total para '{termo_digitado}' ---")
        
        termo_para_arquivo = re.sub(r'[^\w\s-]', '', termo_digitado).replace(' ', '_').lower()
        csv_file_path = f'noticias_otempo_{termo_para_arquivo}_separado.csv' 

        try:
            fieldnames = ['titulo', 'subtitulo', 'data_pura', 'horario', 'link_noticia', 
                          'texto_completo', 'link_imagem_principal', 'tem_video', 'nome_reporter', 'tags_noticia']

            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(noticias_raspadas) 
            print(f"\nDados salvos com sucesso em '{csv_file_path}'")
        except Exception as e:
            print(f"\nErro ao salvar os dados no arquivo CSV: {e}")

        print("\nCaptura de dados concluída. ") 
        print(f"As informações estão salvas em um arquivo CSV: '{csv_file_path}'.")
        print("Agora você pode utilizar os dados em sua pesquisa!")
        print("Bons estudos!")
    else:
        print(f"\nNenhuma notícia foi raspada para o termo '{termo_digitado}'.")
        print("Captura de dados finalizada.")