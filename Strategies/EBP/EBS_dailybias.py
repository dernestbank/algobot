#!/usr/bin/env python3
"""
EBP (Engulfing Bar Play) Strategy for MetaTrader5

This script scans historical daily price data for bullish or bearish engulfing bars,
checks for the “power of three” confirmation on the subsequent candle, and places a trade
if the conditions are met.

Strategy Overview:
    - Bullish Engulfing:
        * Condition: The current candle's low is below the previous candle's low and
          its close is above the previous candle's open.
        * For confirmation, the subsequent candle should have a low at or below the 50%
          retracement level of the engulfing candle’s range and then close above the engulfing candle's high.
    - Bearish Engulfing:
        * Condition: The current candle's high is above the previous candle's high and
          its close is below the previous candle's open.
        * For confirmation, the subsequent candle should have a high at or above the 50%
          retracement level and then close below the engulfing candle's low.
          
The script uses these signals to generate a directional bias and, if conditions are met on the current day,
sends an order via MetaTrader5.

Before using in live trading, backtest thoroughly and adjust risk management parameters.
"""

import MetaTrader5 as mt5
import datetime
import time

# -------------------------------------------------------------------------------
def initialize_mt5():
    """
    Initialize the connection to MetaTrader 5.
    
    Returns:
        bool: True if initialization was successful, False otherwise.
    """
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return False
    return True

# -------------------------------------------------------------------------------
def get_historical_data(symbol: str, timeframe: int, n: int):
    """
    Retrieve historical rates from MetaTrader5.

    Args:
        symbol (str): The trading symbol (e.g., "EURUSD").
        timeframe (int): The timeframe (e.g., mt5.TIMEFRAME_D1 for daily data).
        n (int): Number of bars to retrieve.

    Returns:
        numpy.ndarray: Array of rates (each containing time, open, high, low, close, tick_volume, spread, real_volume).
    """
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    if rates is None:
        print(f"Failed to get historical data for {symbol}")
    return rates

# -------------------------------------------------------------------------------
def is_bullish_engulfing(prev_candle, current_candle) -> bool:
    """
    Check if the current candle forms a bullish engulfing pattern.

    Conditions:
        - Current candle's low is lower than previous candle's low.
        - Current candle's close is higher than previous candle's open.
    
    Args:
        prev_candle (dict/record): The previous candle data.
        current_candle (dict/record): The current candle data.

    Returns:
        bool: True if bullish engulfing condition is met.
    """
    return (current_candle['low'] < prev_candle['low'] and
            current_candle['close'] > prev_candle['open'])

# -------------------------------------------------------------------------------
def is_bearish_engulfing(prev_candle, current_candle) -> bool:
    """
    Check if the current candle forms a bearish engulfing pattern.

    Conditions:
        - Current candle's high is higher than previous candle's high.
        - Current candle's close is lower than previous candle's open.
    
    Args:
        prev_candle (dict/record): The previous candle data.
        current_candle (dict/record): The current candle data.

    Returns:
        bool: True if bearish engulfing condition is met.
    """
    return (current_candle['high'] > prev_candle['high'] and
            current_candle['close'] < prev_candle['open'])

# -------------------------------------------------------------------------------
def check_power_of_three(engulfing_candle, subsequent_candle, trade_direction: str) -> bool:
    """
    Verify the "power of three" condition on the candle following the engulfing bar.

    For bullish confirmation:
        - The subsequent candle's low is at or below the 50% retracement level of the engulfing candle’s range.
        - The subsequent candle closes above the engulfing candle's high.

    For bearish confirmation:
        - The subsequent candle's high is at or above the 50% retracement level.
        - The subsequent candle closes below the engulfing candle's low.

    Args:
        engulfing_candle (dict/record): The engulfing candle data.
        subsequent_candle (dict/record): The candle following the engulfing candle.
        trade_direction (str): 'bullish' or 'bearish'.

    Returns:
        bool: True if the power of three condition is confirmed.
    """
    # Calculate the range and mid-level (50% retracement level) of the engulfing candle
    range_value = engulfing_candle['high'] - engulfing_candle['low']
    mid_level = engulfing_candle['low'] + 0.5 * range_value
    # Define a tolerance relative to the range (this value can be adjusted)
    tolerance = 0.0001 * range_value

    if trade_direction == 'bullish':
        # Check that the subsequent candle dips into the retracement zone and closes above the engulfing high
        if (subsequent_candle['low'] <= mid_level + tolerance and
                subsequent_candle['close'] > engulfing_candle['high']):
            return True
    elif trade_direction == 'bearish':
        # Check that the subsequent candle moves into the retracement zone and closes below the engulfing low
        if (subsequent_candle['high'] >= mid_level - tolerance and
                subsequent_candle['close'] < engulfing_candle['low']):
            return True

    return False

# -------------------------------------------------------------------------------
def place_order(symbol: str, order_type: int, volume: float, price: float, sl: float, tp: float,
                deviation: int = 10, magic: int = 234000):
    """
    Place a market order using MetaTrader5.

    Args:
        symbol (str): Trading symbol.
        order_type (int): mt5.ORDER_TYPE_BUY or mt5.ORDER_TYPE_SELL.
        volume (float): Volume to trade.
        price (float): Order price.
        sl (float): Stop loss price.
        tp (float): Take profit price.
        deviation (int, optional): Allowed price deviation. Defaults to 10.
        magic (int, optional): Magic number to identify the order. Defaults to 234000.

    Returns:
        dict: Result of the order send.
    """
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": magic,
        "comment": "EBP strategy order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    return result

# -------------------------------------------------------------------------------
def main():
    """
    Main function to execute the strategy.
    
    This function:
        1. Retrieves historical daily data for the given symbol.
        2. Scans for bullish or bearish engulfing patterns.
        3. Checks the subsequent candle for a valid power of three confirmation.
        4. Prints detected signals and, if the signal is on the current day, places an order.
    """
    # Parameters (customize as needed)
    symbol = "EURUSD"        # Example symbol; change to your desired instrument
    timeframe = mt5.TIMEFRAME_D1  # Daily timeframe
    volume = 0.1             # Trading volume
    n_bars = 100             # Number of historical bars to retrieve

    # Retrieve historical data
    rates = get_historical_data(symbol, timeframe, n_bars)
    if rates is None or len(rates) < 3:
        print("Not enough data to evaluate the strategy.")
        return

    signals = []  # To store valid signals

    # Iterate over historical data (starting from index 1 to have a previous candle, and ensuring a subsequent candle exists)
    for i in range(1, len(rates) - 1):
        prev_candle = rates[i - 1]
        engulfing_candle = rates[i]
        subsequent_candle = rates[i + 1]

        # Check for bullish engulfing pattern
        if is_bullish_engulfing(prev_candle, engulfing_candle):
            if check_power_of_three(engulfing_candle, subsequent_candle, trade_direction='bullish'):
                # Define stop loss and take profit for bullish trade
                # Stop loss is set slightly below the engulfing candle's low (plus a small buffer)
                buffer = 0.0001 * (engulfing_candle['high'] - engulfing_candle['low'])
                sl = engulfing_candle['low'] - buffer
                risk = subsequent_candle['close'] - sl
                tp = subsequent_candle['close'] + 2 * risk  # Example risk-reward ratio of 1:2

                signals.append({
                    'index': i,
                    'type': 'bullish',
                    'engulfing_time': datetime.datetime.fromtimestamp(engulfing_candle['time']),
                    'entry_time': datetime.datetime.fromtimestamp(subsequent_candle['time']),
                    'entry_price': subsequent_candle['close'],
                    'sl': sl,
                    'tp': tp,
                })

        # Check for bearish engulfing pattern
        elif is_bearish_engulfing(prev_candle, engulfing_candle):
            if check_power_of_three(engulfing_candle, subsequent_candle, trade_direction='bearish'):
                # Define stop loss and take profit for bearish trade
                buffer = 0.0001 * (engulfing_candle['high'] - engulfing_candle['low'])
                sl = engulfing_candle['high'] + buffer
                risk = sl - subsequent_candle['close']
                tp = subsequent_candle['close'] - 2 * risk  # Example risk-reward ratio of 1:2

                signals.append({
                    'index': i,
                    'type': 'bearish',
                    'engulfing_time': datetime.datetime.fromtimestamp(engulfing_candle['time']),
                    'entry_time': datetime.datetime.fromtimestamp(subsequent_candle['time']),
                    'entry_price': subsequent_candle['close'],
                    'sl': sl,
                    'tp': tp,
                })

    # Process signals and, if a signal is from the current day, send a trade order.
    for signal in signals:
        print(f"Signal detected: {signal}")
        # If the entry candle occurred on today's date, attempt to place an order
        if signal['entry_time'].date() == datetime.datetime.now().date():
            order_type = mt5.ORDER_TYPE_BUY if signal['type'] == 'bullish' else mt5.ORDER_TYPE_SELL
            result = place_order(symbol, order_type, volume, signal['entry_price'],
                                 signal['sl'], signal['tp'])
            print("Order result:", result)

# -------------------------------------------------------------------------------
if __name__ == "__main__":
    if initialize_mt5():
        try:
            main()
        finally:
            mt5.shutdown()
