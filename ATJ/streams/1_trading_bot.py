import sys
sys.path.insert(0, r'C:\Users\derne\OneDrive - The Pennsylvania State University\Programming\Extra\algobot\ATJ-algo')



import MetaTrader5 as mt5
from time import sleep
# from ..config_template import login, password, server
from mt5_trade_utils import send_market_order, close_all_positions

from dotenv import load_dotenv
import os

load_dotenv()       
login = os.getenv('login2')
password = os.getenv('password2')
server = os.getenv('server2')



if __name__ == '__main__':
    
    mt5.initialize()
    
    mt5.login(login, password, server)

    sleep(5) # wait for 5 secs to buy

    symbol = 'EURUSDm'
    volume = 1.0
    order_type = 'buy'

    send_market_order(symbol, volume, order_type)

    sleep(5) # after buy close all position in 5 secs 

    close_all_positions('all')