import sys
sys.path.insert(0, r'C:\Users\derne\OneDrive - The Pennsylvania State University\Programming\Extra\algobot\ATJ-algo')

import MetaTrader5 as mt5
import pandas as pd
from time import sleep
from datetime import datetime
from mt5_trade_utils import send_market_order, close_all_positions, get_positions


# load env viriables
from dotenv import load_dotenv
import os
load_dotenv()       
login = os.getenv('login2')
password = os.getenv('password2')
server = os.getenv('server2')

if __name__ == '__main__':
    mt5.initialize()
    
    mt5.login(login, password, server)
    
    
    # strategy parameters
    symbol = 'BTCUSDm'
    time_frame = mt5.TIMEFRAME_M1
    period = 20
    magic = 1
    volume = 0.1

    # sleep to switch to MT5 platform manually to check execution
    sleep(5)
    
    
    # trade logic
    trading_allowed = True
    while trading_allowed:

        # calculate sma
        rates = mt5.copy_rates_from_pos(symbol, time_frame, 1, 20)
        rates_df = pd.DataFrame(rates)

        sma = rates_df['close'].mean()

        # calculate last_close
        last_close = rates_df.iloc[-1]['close']

        print('time', datetime.now(), '|', 'sma', sma, '|', 'last_close', last_close)

        # retrieving positions by magic
        positions = get_positions(magic=magic)

        # separating positions into buy and sell orders
        num_buy_positions = positions[positions['type'] == mt5.ORDER_TYPE_BUY].shape[0]
        num_sell_positions = positions[positions['type'] == mt5.ORDER_TYPE_SELL].shape[0]
        
        
        if last_close > sma:
            # close sell positions
            if num_sell_positions > 0:
                close_all_positions('sell', magic=magic)

            # open buy positions
            if num_buy_positions == 0:
                send_market_order(symbol, volume, 'buy', magic=magic)

        elif last_close < sma:
            # close buy positions
            if num_buy_positions > 0:
                close_all_positions('buy', magic=magic)

            # open sell positions
            if num_sell_positions == 0:
                send_market_order(symbol, volume, 'sell', magic=magic)

        sleep(1)




