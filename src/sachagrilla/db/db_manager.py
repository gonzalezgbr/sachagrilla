# dbmanager.py

import sys
from datetime import datetime
from typing import Optional, Tuple, Dict, List, NamedTuple
from peewee import IntegrityError, fn

from sachagrilla.db.models import Word, Clue, Quote, Control, Grid, GridLine, get_db


class DBManager:
    """Proporciona funciones específicas para interactuar con la BD."""

    def __init__(self):
        self.db = get_db()
        self.db.connect()

    def close(self):
        """Cierra la conexión a la BD."""
        self.db.close()

    def create_tables(self):
        """Crea las tablas."""
        self.db.create_tables([Word, Clue, Quote, Control, Grid, GridLine])
        print('Tablas creadas!')

    def check_tables(self) -> bool:
        """Chequea si las tablas ya existen."""
        ex_tables = self.db.get_tables()
        all_tables = ['word', 'clue', 'quote', 'control', 'grid', 'gridline']

        return any([True for table in all_tables if table in ex_tables])

    def save_word(self, word: str, clue: str) -> Optional[Tuple[Word, Clue]]:
        """Guarda palabra+significado en la BD."""
        # print(f"BEFORE SAVE {word} {clue}")
        now = datetime.now()
        try:
            w = Word.create(content=word, length=len(word), created_at=now)
            c = Clue.create(content=clue, word_id=w.id, created_at=now)
            # print(f"AFTER SAVE {w.id} {w.content} {c.id} {c.content}")
            return w, c
        except IntegrityError as e:
            print(f'WARNING: Palabra + Significado "{word}: {clue}" existente, no insertados!', file=sys.stderr)

    def save_quote(self, content: str, author: str, extra: str = '') -> Optional[Quote]:
        """Guarda frase en la BD."""
        now = datetime.now()
        try:
            q = Quote.create(content=content, author=author, extra=extra, created_at=now)
            return q
        except IntegrityError:
            print(f'WARNING: Frase "{content}" existente, no insertada!', file=sys.stderr)

    @property
    def grid_last_number(self) -> int:
        """Número de grid por el cual iniciar el scraping de claringrilla o último número de grilla en BD."""
        query = Control.select().order_by(Control.id.desc()).limit(1)
        if query:
            return query[0].last_grid_nbr
        else:
            return 18874

    @grid_last_number.setter
    def grid_last_number(self, number: int):
        """Guarda el último número de grilla scrapeada."""
        now = datetime.now()
        c = Control.create(last_grid_nbr=number, created_at=now)
        print(f'>>> N° de última grilla scrapeada guardado: {number}')

    def get_random_quote(self):
        """Devuelve una frase random de la BD."""
        quote = Quote.select(Quote.id, Quote.content).order_by(fn.Random()).limit(1)
        return quote[0]

    @staticmethod
    def get_words(min_length: int) -> Dict[int, str]:
        """Devuelve las palabras de longitud mínima min_length."""
        words = Word.select(Word.id, Word.content).join(Clue, on=(Word.id == Clue.word_id))\
            .where(Word.length >= min_length)
        words_dict = {word.id: word.content for word in words}
        return words_dict

    @staticmethod
    def get_shorter_words(max_length: int) -> Dict[int, str]:
        """Devuelve las palabras de longitud mínima min_length."""
        words = Word.select(Word.id, Word.content).join(Clue, on=(Word.id == Clue.word_id))\
            .where(Word.length <= max_length)
        words_dict = {word.id: word.content for word in words}
        return words_dict

    @staticmethod
    def find_clue(word_id: int) -> Optional[Clue]:
        """Devuelve clue de la palabra con id=id."""
        return Clue.get_or_none(Clue.word_id == word_id)

    @staticmethod
    def save_grid(solution: List[Dict], quote_id: int, position1: int, position2: int) -> int:
        """Toma una solución y la guarda en la BD."""
        now = datetime.now()
        g = Grid.create(quote_id=quote_id, position1=position1, position2=position2, created_at=now)
        for idx, line in enumerate(solution):
            gl = GridLine.create(grid_id=g, row_nbr=idx, word_id=line['word_id'], clue_id=line['clue_id'], created_at=now)
        print('>>> Grilla guardada en la BD para la posteridad.')
        return g

    @staticmethod
    def find_solution(grid_id: int):
        """Toma un grid_id y devuelve la solución para esa grilla."""
        solution = Grid.select(Grid, Quote.content.alias('quote'), Quote.author,
                               GridLine.row_nbr, Word.content.alias('word'), Clue.content.alias('clue'))\
            .join(Quote, on=(Grid.quote_id == Quote.id))\
            .join(GridLine, on=(GridLine.grid_id == Grid.id))\
            .join(Word, on=(Word.id == GridLine.word_id))\
            .join(Clue, on=(Clue.id == GridLine.clue_id))\
            .where(Grid.id == grid_id).dicts()
        return solution

    @staticmethod
    def get_available_grids():
        """Devuelve los ids de las grillas existentes en la BD."""
        available_grids = Grid.select(Grid.id)
        available_grids_str = ' - '.join([str(grid.id) for grid in available_grids])
        return available_grids_str


if __name__ == '__main__':

    dbm = DBManager()
    print(dbm.db)
    q = dbm.get_random_quote()
    for item in q:
        print(item)
