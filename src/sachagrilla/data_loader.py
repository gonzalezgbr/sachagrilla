# dataloader.py

from pathlib import Path
import csv

from sachagrilla.db.db_manager import DBManager
from sachagrilla import MAIN_MODULE_BASEPATH


class DataLoader:
    """Carga palabras y frases de los .csv scrapeados y los guarda en la BD."""

    def __init__(self):
        self.scraped_data_path = MAIN_MODULE_BASEPATH / 'data/scraped'
        self.dbmanager = DBManager()

    def load_quotes(self):
        """Lee todos los *quote.csv de carpeta scraped y almacena las frases en BD. Borra files procesados."""

        all_files = list(self.scraped_data_path.glob('*quote.csv'))
        all_files_quan = len(all_files)
        print(f'>>> Se encontraron {all_files_quan} archivos de frases para procesar.')

        loaded_files = 0
        for file in all_files:
            with open(file, encoding='utf8') as f:
                csv_reader = csv.DictReader(f)
                for line in csv_reader:
                    if self.dbmanager.save_quote(line['QUOTE'], line['AUTHOR']):
                        loaded_files += 1
            Path(file).unlink()

        print(f'>>> Se cargaron {loaded_files} archivos de un total de {all_files_quan}.')

    def load_words(self):
        """Lee todos los *words.csv de carpeta scraped y almacena palabra+significado en BD. Borra files procesados."""

        all_files = list(self.scraped_data_path.glob('*words.csv'))
        all_files_quan = len(all_files)
        print(f'>>> Se encontraron {all_files_quan} archivos de palabra-significado para procesar.')

        loaded_files = 0
        error = True
        for file in all_files:
            with open(file, encoding='utf8', newline='') as f:
                csv_reader = csv.DictReader(f)
                for line in csv_reader:
                    # print(f"ON DATA LOADER {line['WORD']} {line['CLUE']}")
                    if self.dbmanager.save_word(line['WORD'], line['CLUE']):
                        error = False
                loaded_files += 1
            Path(file).unlink()

        print(f'>>> Se cargaron {loaded_files} archivos de un total de {all_files_quan}.')
