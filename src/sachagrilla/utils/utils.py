# utils.py

""" Proporciona funciones auxiliares para procesar el texto durante la generación de la grilla. """

from typing import List, Tuple
import math
import random
import re

from sachagrilla.utils.separasilabas import silabizer


def clean_text(text: str) -> str:
    """Toma un texto y lo devuelve en minúscula y sin signos de puntuación ni acentuación."""
    patterns = [u'[àáâãäå]', u'[èéêë]', u'[ìíîï]', u'[òóôõö]', u'[ùúûü]', u'[,.:;]']
    vowels = ['a', 'e', 'i', 'o', 'u', '']
    for idx, pattern in enumerate(patterns):
        text = re.sub(pattern, vowels[idx], text)
    return text.lower()


def cut_in_half(text: str) -> Tuple[str, str]:
    """Toma un texto, devuelve dos mitades sin espacios. Si la longitud es impar la primera mitad será la más larga."""
    clean_quote = clean_text(text).replace(' ', '').replace(' ', '')
    size = len(clean_quote)
    cut_point = size//2 if size % 2 == 0 else math.ceil(size/2)
    return clean_quote[:cut_point], clean_quote[cut_point:]


def get_random_word(words, pos1, pos2, letter1, letter2):
    """Devuelve una palabra aleatoria cuyas letras en las posiciones señaladas coincidan con las indicadas."""
    if letter2:
        eligible_words = [(idx, word) for idx, word in words.items()
                          if clean_text(word[pos1]) == letter1 and clean_text(word[pos2]) == letter2]
    else:
        eligible_words = [(idx, word) for idx, word in words.items() if clean_text(word[pos1]) == letter1]
    try:
        chosen_word = random.choice(eligible_words)
        return chosen_word
    except IndexError:
        return None, None


def get_all_syllables(words: List[str]) -> str:
    """Toma lista de palabras y devuelve un str con las sílabas de todas las palabras ord. alf. y separadas por coma."""
    syllabator = silabizer()
    syllables = []
    for word in words:
        syllables.extend(syllabator(word))
    syllables = sorted([str(sil) for sil in syllables])
    syllables_str = ', '.join(syllables)
    return syllables_str


if __name__ == '__main__':
    one = [3,3,3]
    two = [9,9, 9]
    for uno, dos in zip(one, two):
        print(uno, dos)
    # print(cut_in_half('seis treso'))