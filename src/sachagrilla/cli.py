# cli.py

"""Proporciona la interfaz de línea de comandos de sachagrilla."""

import argparse
import random
import sys

from sachagrilla.grid import Grid
from sachagrilla.data_collector import collect_data


def add_args(p: argparse.ArgumentParser):
    """Agrega los subparsers de cada comando, con sus argumentos y funciones default."""

    subparsers = p.add_subparsers(help='', dest='subparser')
    parser_new = subparsers.add_parser('nueva', help='Genera una grilla nueva')
    parser_new.add_argument('-s', '--solucion', action='store_true', help='Incluye la solución con la grilla')

    parser_solution = subparsers.add_parser('solucion', help='Muestra la solución de una grilla existente.')
    parser_solution.add_argument('nbr', type=int, help='Número de grilla')
    parser_solution.set_defaults(func=Grid.print_solution)

    parser_collect = subparsers.add_parser('recolectar',
                                              help='Recolecta palabras y su significado y frases de la web.')
    parser_collect.add_argument('-c', '--cantidad', type=int, default=5, help='Cantidad de datos a descargar')
    parser_collect.set_defaults(func=collect_data)

    # parser_stats = subparsers.add_parser('stats', help='Muestra estadísticas de uso de la app.')
    # parser_stats.set_defaults(func=Grid.get_solution)


def main():
    """Crea e invoca el parser de la cli, y direcciona a la función de cada comando."""
    positions = [(0, 2), (0, 3), (0, 4), (0, 5)
                 , (1, 3), (1, 4), (1, 5)
                 , (2, 4), (2, 5), (2, 6)]
    p = argparse.ArgumentParser()
    add_args(p)
    args = p.parse_args()
    print('>>> BIENVENIDO A SACHAGRILLA!')
    if args.subparser == 'nueva':
        print('>>> Generando sachagrilla...')
        g = Grid()
        position = random.choice(positions)
        grid_id = g.build(position[0], position[1])
        attempts = 1
        while grid_id == 0 and attempts < 10:
            attempts += 1
            print(f'>>> ... intento {attempts}...')
            position = random.choice(positions)
            grid_id = g.build(position[0], position[1])
        if grid_id != 0:
            Grid.print(grid_id, args)
        else:
            print('WARNING Esta grilla estaba muy difícil... Intente nuevamente!', file=sys.stderr)
    else:
        args.func(args)
    print('>>> GRACIAS POR USAR SACHAGRILLA! QUE NUNCA TE FALTEN LAS PALABRAS ┑(^_^)┍')


if __name__ == '__main__':
    main()
