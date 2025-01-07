import MetaTrader5 as mt5
import pandas as pd
from time import sleep



def market_order(symbol, volume, order_type, deviation=20, magic=30, stoploss=0.0, take_profit=0.0,
                 strategy_name='Candlestick Bot'):

    """
    Places a market order on the MetaTrader 5 platform.

    Parameters:
    symbol (str): The trading symbol for which the order is placed.
    volume (float): The number of lots for the order.
    order_type (str): The type of order, either 'buy' or 'sell'.
    deviation (int, optional): The maximum price deviation in points. Default is 20.
    magic (int, optional): The magic number to identify the order. Default is 30.
    stoploss (float, optional): The stop loss price level. Default is 0.0.
    take_profit (float, optional): The take profit price level. Default is 0.0.
    strategy_name (str, optional): The comment or name of the strategy. Default is 'Candlestick Bot'.

    Returns:
    order_result: The result of the order operation.
    """

    order_type_dict = {
        'buy': mt5.ORDER_TYPE_BUY,
        'sell': mt5.ORDER_TYPE_SELL
    }

    price_dict = {
        'buy': mt5.symbol_info_tick(symbol).ask,
        'sell': mt5.symbol_info_tick(symbol).bid
    }

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,  # FLOAT
        "type": order_type_dict[order_type],
        "price": price_dict[order_type],
        "sl": stoploss,  # FLOAT
        "tp": take_profit,  # FLOAT
        "deviation": deviation,  # INTERGER
        "magic": magic,  # INTERGER
        "comment": strategy_name,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,  # mt5.ORDER_FILLING_FOK if IOC does not work
    }

    order_result = mt5.order_send(request)
    return (order_result)




def find_engulfing_pattern(candle):
    #see notes in no_git/candlestick_bot.py
    bull_cond1 = candle['close'] > candle['open']  # bull candle condition
    bull_cond2 = candle['close'] > candle['previous_high']  # engulfment condition
    bull_cond3 = candle['previous_open'] > candle['previous_close']  # previous candle must be a bear candle

    bear_cond1 = candle['close'] < candle['open']  # bear candle condition
    bear_cond2 = candle['close'] < candle['previous_low']  # engulfment condition
    bear_cond3 = candle['previous_open'] < candle['previous_close']  # previous candle must be a bull candle

    # special condition - engulfing candle body is 1.5 times as long as previous candle range
    if candle['previous_high'] - candle['previous_low'] == 0:
        return False

    special_cond = abs(candle['open'] - candle['close']) / (candle['previous_high'] - candle['previous_low']) >= 1.5

    if bull_cond1 and bull_cond2 and bull_cond3 and special_cond:
        return 'buy'
    elif bear_cond1 and bear_cond2 and bear_cond3 and special_cond:
        return 'sell'
    else:
        return False



def get_engulfing_signal(symbol, timeframe):
    ohlc = mt5.copy_rates_from_pos(symbol, timeframe, 1, 2) #get the last two candles (current and previous) (symbol, timeframe, position, count)
    ohlc_df = pd.DataFrame(ohlc)[['time', 'open', 'high', 'low', 'close']]
    ohlc_df['time'] = pd.to_datetime(ohlc_df['time'], unit='s')

    ohlc_df['previous_open'] = ohlc_df['open'].shift(1)
    ohlc_df['previous_high'] = ohlc_df['high'].shift(1)
    ohlc_df['previous_low'] = ohlc_df['low'].shift(1)
    ohlc_df['previous_close'] = ohlc_df['close'].shift(1)

    ohlc_df['signal'] = ohlc_df.apply(find_engulfing_pattern, axis=1)

    print(ohlc_df)
    return ohlc_df.iloc[-1]['signal']


if __name__ == '__main__':
    # connect to MetaTrader5 Terminal
    mt5.initialize()

    # login to your Trading Account 
    login = 192918303
    password = "Demo@1234"
    server = "Exness-MT5Trial"

    mt5.login(login, password, server)

    # strategy parameters
    symbol = 'EURUSD'  # plan is to make this multiple instruments
    timeframe = mt5.TIMEFRAME_M1
    volume = 0.01   # plan is to make this dynamic

    trading_allowed = True  # plan is to make this dynamic
    # ---------------To create a troubleshooting function that will avod infinite loop----------------
    #--------------- To create a function that will close the position after a certain time/ condition ------------
    while trading_allowed:
        # Careful! Loop can open infinite positions!

        signal = get_engulfing_signal(symbol, timeframe)
        print('signal', signal)
        print('---\n')

        if signal == 'buy' and mt5.positions_total() == 0:
            res = market_order(symbol, volume, 'buy')
            trading_allowed = False

        elif signal == 'sell' and mt5.positions_total() == 0:
            res = market_order(symbol, volume, 'sell')
            trading_allowed = False

        sleep(1)




