import re
from collections import Counter
import pandas as pd
from nltk.corpus import stopwords
from nltk.util import ngrams
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import platform

# --- Module-level constants and configurations ---

# Define a default set of custom stopwords
CUSTOM_STOPWORDS = {
    'tempo', 'de acordo', 'noticia', 'notícias', 'diz', 'vai', 'pode', 'anos',
    'um', 'uma', 'dois', 'duas', 'ser', 'ter', 'fazer', 'são', 'deve', 'feira',
    'conforme', 'segundo', 'em', 'para', 'com', 'foi', 'sobre'
}

def _configure_matplotlib_font():
    """Configures Matplotlib to use a font that supports accents."""
    try:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    except Exception:
        if 'Windows' in platform.system():
            try:
                plt.rcParams['font.family'] = 'Arial'
            except Exception as e:
                print(f"Aviso: Não foi possível configurar a fonte. Gráficos podem ter problemas de acentuação. Erro: {e}")

_configure_matplotlib_font()


def _get_stopwords():
    """Downloads (if necessary) and returns a set of Portuguese stopwords."""
    try:
        stop_words = set(stopwords.words('portuguese'))
    except LookupError:
        print("Baixando a lista de stopwords do NLTK (necessário apenas na primeira execução)...")
        nltk.download('stopwords')
        stop_words = set(stopwords.words('portuguese'))
    stop_words.update(CUSTOM_STOPWORDS)
    return stop_words

def _clean_and_tokenize(text, stop_words):
    """Cleans and tokenizes text, removing stopwords and short words."""
    if not isinstance(text, str):
        return []
    clean_text = re.sub(r'[^a-zA-ZáéíóúãõâêôàçüÁÉÍÓÚÃÕÂÊÔÀÇÜ\s-]', '', text).lower()
    words = clean_text.split()
    return [word for word in words if word not in stop_words and len(word) > 2]

# --- Public API Functions ---

def get_ngram_frequency(text_series: pd.Series, n: int, top_n: int = 50):
    """
    Calculates the frequency of n-grams in a pandas Series of text.

    Args:
        text_series (pd.Series): A Series containing the text to analyze.
        n (int): The "n" in n-gram (1 for unigram, 2 for bigram, etc.).
        top_n (int): The number of most common n-grams to return.

    Returns:
        A list of tuples, where each tuple is (n-gram, frequency).
    """
    stop_words = _get_stopwords()
    all_ngrams = []
    for text in text_series.dropna():
        words = _clean_and_tokenize(text, stop_words)
        if len(words) >= n:
            current_ngrams = list(ngrams(words, n))
            all_ngrams.extend([' '.join(gram) for gram in current_ngrams])

    return Counter(all_ngrams).most_common(top_n)

def get_tag_frequency(tags_series: pd.Series, top_n: int = 50):
    """
    Calculates the frequency of tags from a comma-separated string Series.

    Args:
        tags_series (pd.Series): A Series containing comma-separated tags.
        top_n (int): The number of most common tags to return.

    Returns:
        A list of tuples, where each tuple is (tag, frequency).
    """
    all_tags = []
    for tags_str in tags_series.dropna():
        tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip() and tag.lower() != 'n/a']
        all_tags.extend(tags_list)

    return Counter(all_tags).most_common(top_n)

def create_wordcloud(text_series: pd.Series, output_path: str):
    """
    Generates and saves a word cloud image from a text Series.

    Args:
        text_series (pd.Series): The text data to visualize.
        output_path (str): The path to save the generated image file.
    """
    stop_words = _get_stopwords()
    full_text = ' '.join(text_series.fillna('').astype(str).tolist())

    if not full_text.strip():
        print(f"Não há texto para gerar a nuvem de palavras. Pulando salvamento de '{output_path}'.")
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
    plt.title(f"Nuvem de Palavras: {text_series.name}")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Nuvem de palavras salva em: {output_path}")

def create_barchart(freq_data: list, title: str, output_path: str, top_n: int = 20):
    """
    Generates and saves a horizontal bar chart from frequency data.

    Args:
        freq_data (list): A list of (label, value) tuples.
        title (str): The title for the chart.
        output_path (str): The path to save the generated image file.
        top_n (int): The number of items to display in the chart.
    """
    if not freq_data:
        print(f"Não há dados para gerar o gráfico de barras '{title}'. Pulando.")
        return

    # Take the top N items and reverse for correct plotting order
    labels = [item[0] for item in freq_data[:top_n]][::-1]
    counts = [item[1] for item in freq_data[:top_n]][::-1]

    plt.figure(figsize=(12, 8))
    plt.barh(labels, counts, color='skyblue')
    plt.xlabel("Frequência")
    plt.ylabel("Termos")
    plt.title(title)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Gráfico de barras salvo em: {output_path}")
