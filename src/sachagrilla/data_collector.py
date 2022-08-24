# datacollector.py

""" Administra el scraping de los datos según las opciones ingresadas por cli. """

from argparse import Namespace

from sachagrilla.data_loader import DataLoader
from sachagrilla.db.db_manager import DBManager
from sachagrilla.scrapers.scraper_clarin import ScraperClarin


def collect_data(args: Namespace):
    """ Hace los llamados necesarios para scrapear data y almacenarla en la BD. """
    cantidad = args.cantidad
    dbm = DBManager()
    if not dbm.check_tables():
        dbm.create_tables()

    r = ScraperClarin(dbm.grid_last_number)
    new_last_number = r.scrape_data(cantidad)
    dbm.grid_last_number = new_last_number

    dl = DataLoader()
    dl.load_quotes()
    dl.load_words()
    dbm.close()
