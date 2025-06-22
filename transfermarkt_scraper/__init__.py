import logging
import azure.functions as func
from transfermarkt_scraper import Transfermarkt
import datetime
import pandas as pd

def main(mytimer: func.TimerRequest) -> None:
    scraper = Transfermarkt()
    player_id = '28003'  # Ejemplo
    df = scraper.get_player_market_value(player_id)
    df.to_csv(f'/tmp/{player_id}_{datetime.date.today()}.csv', index=False)
    logging.info(f"Scrapeo exitoso para {player_id}")
