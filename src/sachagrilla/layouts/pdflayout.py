# pdflayout.py

from datetime import date
from pathlib import Path
from typing import Dict

from fpdf import FPDF

from sachagrilla.utils.utils import get_all_syllables


class PDFLayout:
    """Proporciona funciones para generar los pdfs de grillas y sus soluciones."""

    def __init__(self, solution: Dict):
        self.pdf = FPDF()
        self.pdf.set_margins(left=15, top=10)
        self.pdf.set_auto_page_break(False, margin=1)
        self.pdf.add_font('Ink Free', '', r'C:\Windows\Fonts\Inkfree.ttf', uni=True)
        self.pdf.add_font('Calibri Light', '', r'C:\Windows\Fonts\calibril.ttf', uni=True)
        self.output_path = Path('data/grids/')
        self.solution = solution
        self.grid_id = solution[0]['id']
        self.x_clue_box = 0
        self.y_clue_box = 0
        self.y_syllables_box = 0
        self.y_clues_box_end = 0

    def header(self):
        """Escribe el header del pdf. """
        self.pdf.set_y(20)
        title = f'SACHAGRILLA N° {self.grid_id}'
        self.pdf.set_font("Ink Free", size=24)
        self.pdf.cell(0, self.pdf.font_size+4, txt=title, border=0, ln=2, align='C')
        self.pdf.ln()

    def footer(self):
        """Escribe el footer del pdf."""
        self.pdf.set_y(-20)
        self.pdf.set_font('Ink Free', size=7)
        self.pdf.cell(0, 10, 'SachaGrilla App By GG | github.com@gonzalezgbr', 0, 0, align='R')

    def draw_grid(self):
        """Dibuja la grilla tomando los datos de la BD."""
        self.y_clue_box = self.pdf.get_y()
        max_word_length = 0
        square_size = 8
        for idx, grid_line in enumerate(self.solution):
            word_length = len(grid_line['word'])
            if word_length > max_word_length:
                max_word_length = word_length
            self.pdf.set_font_size(size=8)
            if idx % 2 == 0:
                self.pdf.set_fill_color(r=240)
            else:
                self.pdf.set_fill_color(r=200)
            self.pdf.cell(square_size, square_size, txt=str(idx + 1), fill=True, align='R')
            # self.pdf.set_font("BookmanOldStyle", size=12)
            self.pdf.set_font_size(size=12)
            self.pdf.set_fill_color(r=255, g=230, b=153)
            self.pdf.set_draw_color(r=112, g=112, b=112)
            for column in range(word_length):
                if column == grid_line['position1'] or column == grid_line['position2']:
                    self.pdf.cell(square_size, square_size, txt='', border=1, fill=True)
                else:
                    self.pdf.cell(square_size, square_size, '', border=1)
            self.pdf.ln(square_size)
        self.x_clue_box = (max_word_length + 4) * square_size
        self.y_syllables_box = self.pdf.get_y()

    def draw_clues(self):
        """Dibuja la caja con las definiciones de las palabras de la grilla."""
        self.pdf.set_xy(self.x_clue_box, self.y_clue_box)
        self.pdf.cell(0, self.pdf.font_size + 3, 'DEFINICIONES', ln=2, border='LRT')
        self.pdf.set_font("Calibri Light", size=9)
        for idx, grid_line in enumerate(self.solution):
            self.pdf.multi_cell(0, self.pdf.font_size + 2, str(idx + 1) + ': ' + grid_line['clue'], border='LR')
            self.pdf.set_x(self.x_clue_box)
        else:
            self.pdf.cell(0, self.pdf.font_size + 3, '', ln=2, border='T')
        self.y_clues_box_end = self.pdf.get_y()

    def draw_syllables(self):
        """Dibuja la caja con las sílabas de las palabras de la grilla."""
        self.pdf.set_x(15)
        # posicionar debajo de la caja más larga (grilla o definiciones)
        if self.y_clues_box_end > self.y_syllables_box:
            self.pdf.set_y(self.y_clues_box_end+10)
        else:
            self.pdf.set_y(self.y_syllables_box+10)

        self.pdf.set_font("Ink Free", size=12)
        self.pdf.cell(0, self.pdf.font_size + 3, 'SÍLABAS', ln=2, border='LRT')
        self.pdf.set_font("Calibri light", size=9)
        words = [grid_line['word'] for grid_line in self.solution]
        syllables = get_all_syllables(words)
        self.pdf.multi_cell(0, self.pdf.font_size + 3, syllables, border='LRB')

    def draw_solution(self, with_grid: bool):
        """Dibuja la caja de la solución. Las palabras van escritas al revés."""
        self.pdf.set_x(15)
        if with_grid:
            self.pdf.set_y(-30)
        self.pdf.set_font("Ink Free", size=8)
        self.pdf.line(self.pdf.get_x(), self.pdf.get_y(), self.pdf.get_x()+180, self.pdf.get_y())
        self.pdf.cell(0, self.pdf.font_size + 2, 'SOLUCIÓN', ln=2, border=0)
        self.pdf.set_font("Calibri Light", size=6)
        words_reversed = [f"{grid_line['row_nbr']+1}: {grid_line['word'][::-1]}" for grid_line in self.solution]
        words_reversed_str = ' - '.join(words_reversed)
        self.pdf.multi_cell(0, self.pdf.font_size + 1, words_reversed_str, border=0)
        quote_reversed = self.solution[0]['quote'][::-1]
        self.pdf.multi_cell(0, self.pdf.font_size + 1, f'"{quote_reversed}"', border=0)

    def print_grid(self, include_solution: bool) -> Path:
        """Interfaz pública. Llama a los métodos necesarios para imprimir la grilla, con o sin solución"""
        print('>>> Generando un pdf bonito y prolijo...')
        self.pdf.add_page()
        self.header()
        self.draw_grid()
        self.draw_clues()
        self.draw_syllables()
        if include_solution:
            self.draw_solution(True)
        self.footer()
        today = str(date.today())
        pdf_name = f'SachaGrilla-{self.grid_id}_{today}.pdf'
        self.pdf.output(self.output_path / pdf_name)
        print('>>> PDF listo para rayar!')
        return self.output_path / pdf_name

    def print_solution(self) -> Path:
        """Interfaz pública. Llama a los métodos necesarios para la solución de una grilla"""
        print('>>> Generando pdf con solución de sachagrilla ...')
        self.pdf.add_page()
        self.header()
        self.draw_solution(False)
        self.footer()
        today = str(date.today())
        pdf_name = f'SachaGrilla-{self.grid_id}_solucion_{today}.pdf'
        self.pdf.output(self.output_path / pdf_name)
        print('>>> PDF con solución listo!')
        return self.output_path / pdf_name


if __name__ == '__main__':
    pass
