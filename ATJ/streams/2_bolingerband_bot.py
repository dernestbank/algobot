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
    symbol = 'XAUUSDm'
    time_frame = mt5.TIMEFRAME_M5
    period = 20
    magic = 2
    volume = 0.1
    num_deviations = 2

    # sleep to switch to MT5 platform manually to check execution
    sleep(5)
    
    
    # trade logic
    trading_allowed = True
    while trading_allowed:
        # calculate sma
        rates = mt5.copy_rates_from_pos(symbol, time_frame, 1, 20)
        rates_df = pd.DataFrame(rates)

        sma = rates_df['close'].mean()
        standard_deviation = rates_df['close'].std()
        upper_band = sma + num_deviations * standard_deviation
        lower_band = sma - num_deviations * standard_deviation

        # calculate last_close
        last_close = rates_df.iloc[-1]['close']

        print('time', datetime.now(), '|', 'sma', sma, '|', 'last_close', last_close, '|',
              'standard deviation', standard_deviation, '|', 'upper band', upper_band, '|',
              'lower band', lower_band)

        open_positions = get_positions(magic=magic)

        if last_close > upper_band and open_positions.empty:
            current_price = mt5.symbol_info_tick(symbol).bid
            sl = current_price + 1 * standard_deviation
            tp = current_price - 1 * standard_deviation

            send_market_order(symbol, volume, 'sell', magic=magic, sl=sl, tp=tp)

        elif last_close < lower_band and open_positions.empty:
            current_price = mt5.symbol_info_tick(symbol).ask
            sl = current_price - 1 * standard_deviation
            tp = current_price + 1 * standard_deviation
            send_market_order(symbol, volume, 'buy', magic=magic, sl=sl, tp=tp)

        sleep(1)