# scraper_clarin.py

from pathlib import Path
from typing import Optional, List, Tuple
import csv

from bs4 import BeautifulSoup
import requests


class ScraperClarin:
    """Proporciona funciones para scrapear los datos de las claringrillas."""

    # FIRST_START = 18874, 1/1/2021
    MARKERS = {
        'CLUE_TAG': 'div',
        'CLUE_CLASS': 'definiciones',
        'WORD_TAG': 'div',
        'WORD_CLASS': 'pull-right col-lg-9 col-md-8 col-sm-6 col-xs-12 words',
        'QUOTE_TAG': 'div',
        'QUOTE_CLASS': 'pull-right col-lg-9 col-md-8 col-sm-6 col-xs-12 words',
    }

    def __init__(self, next_grid_to_scrape: int):
        self.base_url = 'https://www.clarin.com/claringrilla/'
        self.next_grid_to_scrape = next_grid_to_scrape
        self.scraped_data_path = Path(__file__).parent.resolve().joinpath('../data/scraped/')
        # self.scraped_data_path = Path('../data/scraped/')

    def scrape_data(self, nbr_pages: int = 20) -> int:
        """Interfaz pública. Toma número de grillas a scrapear, descarga cada una, extrae data de palabra+significado
        y frase y las almacena en archivos .csv.
        Retorna el número de la grid siguiente a scrapear."""

        start = self.next_grid_to_scrape
        end = start + nbr_pages
        print(f'>>> Iniciando scraping de {nbr_pages} páginas...')

        totals = dict(words=0, clues=0, quotes=0)
        for i in range(start, end):
            current_url = self.base_url + str(i)
            next_url = self.base_url + str(i + 1)
            page = self.get_page(current_url)
            next_page = self.get_page(next_url)
            if page and next_page:
                quote = self.extract_quote(page)
                clues = self.extract_clues(page)
                words = self.extract_words(next_page)
                if clues and words:
                    totals['words'] += len(words)
                    totals['clues'] += len(clues)
                    self.save_to_word_file(words, clues, i)
                if quote:
                    totals['quotes'] += 1
                    self.save_to_quote_file(quote, i)
                print(f'>>> Data de grid {i} extraída y guardada.')
        print(f'>>> Se terminó de scrapear {abs(start-end)} grillas.')
        print(f'>>> Sacamos {totals["quotes"]} frases, {totals["words"]} palabras y {totals["clues"]} significados.')
        return end

    def get_page(self, url: str) -> Optional[str]:
        """Obtiene url, descarga contenido de la página y lo devuelve."""
        r = requests.get(url)
        if r.status_code == 200:
            return r.text

    def extract_clues(self, page: str) -> List[str]:
        """Toma contenido de página html y devuelve una lista de significados."""
        soup = BeautifulSoup(page, 'html.parser')
        tag = soup.find(ScraperClarin.MARKERS['CLUE_TAG'], class_=ScraperClarin.MARKERS['CLUE_CLASS'])
        clues = tag.find_all('p', class_='definition-row')
        clues = self.clean(*[clue.string for clue in clues])
        return clues

    def extract_words(self, page: str) -> List[str]:
        """Toma contenido de página html y devuelve una lista de palabras."""
        soup = BeautifulSoup(page, 'html.parser')
        tag = soup.find(ScraperClarin.MARKERS['WORD_TAG'], class_=ScraperClarin.MARKERS['WORD_CLASS'])
        words = tag.select('div > .col2 > span')[0].string.split(',')
        words = self.clean(*words)
        return words

    def extract_quote(self, page: str) -> Optional[Tuple[str, str]]:
        """Toma contenido de página html y devuelve frase y autor.
        Si la frase es parte de una más larga, la ignora."""
        soup = BeautifulSoup(page, 'html.parser')
        tag = soup.find(ScraperClarin.MARKERS['QUOTE_TAG'], class_=ScraperClarin.MARKERS['QUOTE_CLASS'])
        quote = tag.select('div > .col3 > span')[0].string.strip()
        if 'parte)' not in quote and '(Conclus' not in quote:
            content = quote[1: quote[1:].find('"')+1]
            author = quote[quote[1:].find('"')+1:]
            content, author = self.clean(content, author)
            return content, author

    def clean(self, *args: str) -> List[str]:
        """Elimina puntuación y espacios en blanco marginales de los items recibidos."""
        clean_items = []
        for item in args:
            item = item.strip('\n\r .,"\'')
            clean_items.append(item)
        return clean_items

    def save_to_quote_file(self, quote: Tuple[str, str], grid_number: int):
        """Guarda frase con su autor en un archivo .csv."""
        filename = self.scraped_data_path / (str(grid_number) + '_quote.csv')
        with open(filename, 'w', encoding='utf8', newline='\n') as f:
            writer = csv.writer(f)
            writer.writerow(['QUOTE', 'AUTHOR'])
            writer.writerow([quote[0], quote[1]])

    def save_to_word_file(self, words: List[str], clues: List[str], grid_number: int):
        """Guarda palabra+significado en un archivo .csv."""
        filename = self.scraped_data_path / (str(grid_number) + '_words.csv')
        with open(filename, 'w', encoding='utf8', newline='\n') as f:
            writer = csv.writer(f)
            writer.writerow(['WORD', 'CLUE'])
            for word, clue in zip(words, clues):
                writer.writerow([word, clue])


if __name__ == '__main__':
    sc = ScraperClarin(18874)
    new_last_number = sc.scrape_data(1)
