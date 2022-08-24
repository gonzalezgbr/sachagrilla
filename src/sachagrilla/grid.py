# gridbuilder.py

from argparse import Namespace
from datetime import date
import sys

from sachagrilla.layouts.pdflayout import PDFLayout
from db.db_manager import DBManager
from utils import utils


class Grid:
    """"Proporciona funciones para generar una nueva grilla e imprimirla."""

    def __init__(self):
        self.dbm = DBManager()
        self.quote = ''
        self.words = []
        self.clues = []
        self.date = date.today()

    def build(self, position1: int, position2: int) -> int:
        """Interfaz pública. Construye grilla y la guarda en la BD. Devuelve id de grilla generada o O si falla."""
        try_again = False
        print('>>> Buscando una buena frase...')
        quote = self.dbm.get_random_quote()
        quote_half1, quote_half2 = utils.cut_in_half(quote.content)
        print('>>> Lista la frase perfecta!')
        words = DBManager.get_words(position2+1)
        print('>>> Buscando las palabras adecuadas...')
        solution = []
        for letter_half1, letter_half2 in zip(quote_half1, quote_half2):
            word_id, word = utils.get_random_word(words, position1, position2, letter_half1, letter_half2)
            if not word_id:
                try_again = True
                break
            clue = DBManager.find_clue(word_id)
            solution.append(dict(word_id=word_id, word=word, clue_id=clue.id, clue=clue.content))
        else:
            if len(quote_half1) > len(quote_half2):
                words = DBManager.get_shorter_words(position2+1)
                word_id, word = utils.get_random_word(words, position1, position2, quote_half1[-1], None)
                if not word_id:
                    try_again = True
                else:
                    clue = DBManager.find_clue(word_id)
                    solution.append(dict(word_id=word_id, word=word, clue_id=clue.id, clue=clue.content))
            if try_again:
                return 0
            else:
                print('>>> Las mejores palabras jamás leídas están seleccionadas!')
                grid_id = DBManager.save_grid(solution, quote.id, position1, position2)
                print(f'>>> Sachagrilla N° {grid_id} lista!')
                return grid_id
        if try_again:
            return 0

    @staticmethod
    def print(grid_id: int, args: Namespace):
        """Interfaz pública. Toma un id de grilla y genera el pdf correspondiente."""
        solution = DBManager.find_solution(grid_id)
        print_solution = args.solucion
        pdf_file = PDFLayout(solution).print_grid(print_solution)
        print('file:///' + str(pdf_file.absolute()).replace('\\', '/'))

    @staticmethod
    def print_solution(args: Namespace):
        """Interfaz pública. Toma un id de grilla y genera el pdf solo con la solución."""
        grid_id = args.nbr
        solution = DBManager.find_solution(grid_id)
        if solution:
            pdf_file = PDFLayout(solution).print_solution()
            print('file:///' + str(pdf_file.absolute()).replace('\\', '/'))
        else:
            print(f'WARNING No existe la grilla N° {grid_id}. '
                  f'Genere una grilla nueva o imprima solución de alguna existente.', file=sys.stderr)
            available_grids = DBManager.get_available_grids()
            print(f'>>> Grillas disponibles: {available_grids}')


if __name__ == '__main__':
    pass
