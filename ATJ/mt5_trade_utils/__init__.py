import MetaTrader5 as mt5
import pandas as pd


# function to send a market order
def send_market_order(symbol, volume, order_type, sl=0.0, tp=0.0,
                      deviation=20, comment='', magic=0, type_filling=mt5.ORDER_FILLING_IOC):
    """
    Sends a market order with specified parameters.

    Parameters
    ----------
    symbol : str
        The symbol of the security.
    volume : float
        The number of lots to trade.
    order_type : str
        The type of order, 'buy' or 'sell'.
    sl : float, optional
        The stop loss value. Default is 0.0.
    tp : float, optional
        The take profit value. Default is 0.0.
    deviation : int, optional
        The maximum price deviation in points. Default is 20.
    comment : str, optional
        The comment or name of the strategy. Default is ''.
    magic : int, optional
        The magic number to identify the order. Default is 0.
    type_filling : int, optional
        The type of filling. Default is mt5.ORDER_FILLING_IOC.
        ORDER_FILLING_IOC
        An agreement to execute a deal at the maximum volume available in the market within the volume specified in the order.
        If the request cannot be filled completely, an order with the available volume will be executed, and the remaining volume will be canceled.

    Returns
    -------
    order_result : int
        The result of the order operation.
    """

    tick = mt5.symbol_info_tick(symbol) #get the current tick

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": type_filling,
    }

    order_result = mt5.order_send(request)
    print(order_result.comment)

    return order_result




def close_position(position, deviation=20, magic=0, comment='', type_filling=mt5.ORDER_FILLING_IOC):
    """
    Closes an open position on the MetaTrader 5 platform.

    Parameters
    ----------
    position : dict
        The position to be closed, containing keys 'symbol', 'ticket', 'volume', and 'type'.
    deviation : int, optional
        The maximum price deviation in points. Default is 20.
    magic : int, optional
        The magic number to identify the order. Default is 0.
    comment : str, optional
        A comment for the order. Default is an empty string.
    type_filling : int, optional
        The type of filling. Default is mt5.ORDER_FILLING_IOC.

    Returns
    -------
    order_result : object
        The result of the order operation.
    """

    order_type_dict = {
        0: mt5.ORDER_TYPE_SELL,
        1: mt5.ORDER_TYPE_BUY
    }

    price_dict = {
        0: mt5.symbol_info_tick(position['symbol']).bid,
        1: mt5.symbol_info_tick(position['symbol']).ask
    }

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position['ticket'],  # select the position you want to close
        "symbol": position['symbol'],
        "volume": position['volume'],  # FLOAT
        "type": order_type_dict[position['type']], #to return the reverse of the buy order
        "price": price_dict[position['type']],
        "deviation": deviation,  # INTERGER
        "magic": magic,  # INTERGER
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": type_filling,
    }

    print(request)

    order_result = mt5.order_send(request)
    return (order_result)



def close_all_positions(order_type, magic=None, type_filling=mt5.ORDER_FILLING_IOC):
    """
    Close all open positions with a given order type.

    Parameters
    ----------
    order_type : str
        The type of order to close. 'buy' or 'sell' or 'all' to close all positions.
    magic : int, optional
        The magic number to identify the order. Default is None.
    type_filling : int, optional
        The type of filling. Default is mt5.ORDER_FILLING_IOC.

    Returns
    -------
    result : int
        1 if successful, otherwise 0.
    """

    order_type_dict = {
        'buy': 0,
        'sell': 1
    }

    if mt5.positions_total() > 0:
        positions = mt5.positions_get()

        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())

        # filtering by magic if specified
        if magic:
            positions_df = positions_df[positions_df['magic'] == magic]

        if order_type != 'all':
            positions_df = positions_df[(positions_df['type'] == order_type_dict[order_type])]

        if positions_df.empty:
            print('No open positions')
            return []

        results = []
        for i, position in positions_df.iterrows():
            order_result = close_position(position, type_filling=type_filling)
            print('order_result: ', order_result)
            results.append(order_result)

        return 1
    
    
    
def modify_sl_tp(ticket, stop_loss, take_profit):
    # modify SL/TP

    """
    Modifies the stop loss and take profit levels for an open position.

    Parameters:
    ticket (int): The ticket number of the open position.
    stop_loss (float): The new stop loss price level.
    take_profit (float): The new take profit price level.

    Returns:
    res: The result of the modify SL/TP operation.
    """

    stop_loss = float(stop_loss)
    take_profit = float(take_profit)


    request = {
        'action': mt5.TRADE_ACTION_SLTP,
        'position': ticket,
        'sl': stop_loss,
        'tp': take_profit
    }

    res = mt5.order_send(request)
    return res    



def get_positions(magic=None):
    """
    Retrieves open positions from MetaTrader 5.

    Parameters:
    magic (int): The magic number of the strategy to filter by. If not specified, all open positions are returned.

    Returns:
    positions_df (pd.DataFrame): A pandas DataFrame containing the open positions. The columns are the same as those returned by MetaTrader 5's `positions_get()` function.
    """
    if mt5.positions_total():
        positions = mt5.positions_get()
        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())

        if magic:
            positions_df = positions_df[positions_df['magic'] == magic]

        return positions_df

    else:
        return pd.DataFrame(columns=['ticket', 'time', 'time_msc', 'time_update', 'time_update_msc', 'type',
                                     'magic', 'identifier', 'reason', 'volume', 'price_open', 'sl', 'tp',
                                     'price_current', 'swap', 'profit', 'symbol', 'comment', 'external_id'])
