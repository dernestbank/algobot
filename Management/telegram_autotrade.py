# ```

# • Calculate a market order’s volume so that your stop‐loss distance (the “risk per unit”) multiplies into a total risk equal to 8% of your account equity (unless you include a “Risk” note).

# • Place a market order with no TP attached and store the trade details.
# • In a monitoring thread the bot will check for the first take profit target being reached, and when it does it will modify the trade’s stop loss to your entry price (i.e. breakeven).
# • (You can later expand the code to perform partial closes or to monitor further TP levels.)

# Below is the sample code integrating this functional

# ```
import MetaTrader5 as mt5
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import pandas as pd
import threading
import time


# ---------------------------
# Bot & MT5 Initialization
# ---------------------------
from config import TOKEN2, CHAT_ID2
TELEGRAM_BOT_TOKEN =TOKEN2
CHAT_ID = 803510108

if not mt5.initialize():
    print("Failed to initialize MT5")
    quit()

bot = Bot(token=TELEGRAM_BOT_TOKEN)
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Global dictionary to hold trade management details
# Keys are order tickets and values are details such as TP levels, entry price, etc.
pending_trade_management = {}

# ---------------------------
# Helper: Calculate Lot Size
# ---------------------------
def calculate_lot_size(entry_price: float, stop_loss: float, risk_percent: float) -> float:
    """
    A simplified lot size calculation.
    For a Buy order, risk per unit = entry - stop_loss;
    For a Sell order, risk per unit = stop_loss - entry.
    
    Note: In real trading the calculation must factor in the contract size,
    tick value, and instrument specifics.
    """
    account_info = mt5.account_info()
    if account_info is None:
        return 0.0
    equity = account_info.equity
    risk_amount = equity * risk_percent
    risk_per_unit = abs(entry_price - stop_loss)
    if risk_per_unit == 0:
        return 0.0
    lot_size = risk_amount / risk_per_unit
    return round(lot_size, 2)  # rounding to 2 decimals




# ---------------------------
# /trade_signal Command Handler
# ---------------------------
def trade_signal(update: Update, context: CallbackContext):
    """
    Parses a multi-line text signal of the form:
    
    Gold Buy Now 2936-2933
    
    SL 2930
    
    TP 2939
    TP 2944
    TP Open
    
    Optionally, you can include a risk note (e.g. "Risk 10%").
    """
    try:
        # Get the full message text after the command
        text = update.message.text
        # Remove the command itself (/trade_signal)
        signal_text = text.partition(" ")[2]
        if not signal_text:
            update.message.reply_text("Please provide a trade signal text after /trade_signal.")
            return
        
        # Split into non-empty lines
        lines = [line.strip() for line in signal_text.splitlines() if line.strip()]
        if len(lines) < 3:
            update.message.reply_text("Incomplete signal. Make sure to include symbol/direction, SL, and at least one TP.")
            return

        # ----- Parse first line: symbol, action, and entry range -----
        # Expected format: "Gold Buy Now 2936-2933"
        first_line_parts = lines[0].split()
        if len(first_line_parts) < 4:
            update.message.reply_text("First line must include symbol, action, and entry range (e.g., 'Gold Buy Now 2936-2933').")
            return

        symbol = first_line_parts[0]
        action = first_line_parts[1].lower()  # expecting "buy" or "sell"
        # We assume "Now" is just an indicator; the fourth element is the entry range
        entry_range_str = first_line_parts[3]
        if "-" in entry_range_str:
            try:
                entry_low, entry_high = map(float, entry_range_str.split("-"))
                # For a Buy order, you might prefer a lower entry; for Sell, the higher entry.
                entry_estimate = (entry_low + entry_high) / 2
            except Exception as e:
                update.message.reply_text("Error parsing entry range. Ensure it is in format '2936-2933'.")
                return
        else:
            update.message.reply_text("Entry range must be provided in the format '2936-2933'.")
            return

        # ----- Parse remaining lines for SL, TP(s), and optional Risk -----
        stop_loss = None
        tp_levels = []
        risk_percent = 0.08  # default risk 8%
        for line in lines[1:]:
            parts = line.split()
            if not parts:
                continue
            if parts[0].upper() == "SL":
                try:
                    stop_loss = float(parts[1])
                except:
                    update.message.reply_text("Invalid SL format. Use: SL <price>.")
                    return
            elif parts[0].upper() == "TP":
                tp_val = parts[1]
                if tp_val.lower() == "open":
                    tp_levels.append("open")
                else:
                    try:
                        tp_levels.append(float(tp_val))
                    except:
                        update.message.reply_text("Invalid TP format. Use: TP <price> or TP Open.")
                        return
            elif parts[0].lower() == "risk":
                try:
                    # e.g. "Risk 10%" or "Risk 0.1" (interpreted as 10% if >1)
                    val = parts[1].replace("%", "")
                    risk_val = float(val)
                    # If the value is given as a whole number >1, treat it as percentage
                    risk_percent = risk_val / 100.0 if risk_val > 1 else risk_val
                except:
                    pass  # keep default if parsing fails

        if stop_loss is None or len(tp_levels) == 0:
            update.message.reply_text("Signal must include SL and at least one TP.")
            return

        # ----- Determine Execution Price -----
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            update.message.reply_text(f"Symbol {symbol} not found in MT5.")
            return

        if action == "buy":
            entry_price = tick.ask  # use current ask for Buy
        elif action == "sell":
            entry_price = tick.bid  # use current bid for Sell
        else:
            update.message.reply_text("Action must be 'Buy' or 'Sell'.")
            return

        # ----- Calculate Lot Size Based on Risk -----
        lot_size = calculate_lot_size(entry_price, stop_loss, risk_percent)
        if lot_size <= 0:
            update.message.reply_text("Lot size calculation failed. Check your SL and entry values.")
            return

        # ----- Place the Order (Market Order) -----
        order_type = mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": order_type,
            "price": entry_price,
            "sl": stop_loss,
            "tp": 0.0,  # no TP since we manage multiple TPs manually
            "deviation": 10,
            "magic": 123456,
            "comment": "Trade Signal via Telegram Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            update.message.reply_text(f"Order failed: {result.comment}")
            return

        ticket = result.order
        update.message.reply_text(f"Trade order placed successfully. Ticket: {ticket}\nLot size: {lot_size}\nEntry: {entry_price}\nSL: {stop_loss}\nTP levels: {tp_levels}")

        # ----- Store Trade Details for Ongoing Management -----
        pending_trade_management[ticket] = {
            "tp_levels": tp_levels,  # list of TP targets (first TP is used for breakeven adjustment)
            "entry": entry_price,
            "first_tp_hit": False,
            "action": action,
            "symbol": symbol,
            "lot_size": lot_size,
        }
    except Exception as e:
        update.message.reply_text(f"Error processing trade signal: {str(e)}")

dispatcher.add_handler(CommandHandler("trade_signal", trade_signal))


# ---------------------------
# Enhanced Trade Signal Monitoring Thread
# ---------------------------
def monitor_trade_signals():
    """
    Monitors active trades for TP targets:
      • First TP: Execute a partial close of 50% of the original volume.
      • Second TP: Set the stop loss to the entry price (breakeven) for the remaining position.
      • Subsequent TPs: Execute additional partial closes (e.g., 25% of original volume).
    """
    while True:
        # Iterate over a copy of the pending trades.
        for ticket, details in list(pending_trade_management.items()):
            symbol = details["symbol"]
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                continue

            current_price = tick.ask if details["action"] == "buy" else tick.bid

            if not details["tp_levels"]:
                continue  # No TP levels remaining.

            # Next TP level to check.
            next_tp = details["tp_levels"][0]
            # For numeric TPs, check if current price has reached/exceeded the target.
            if isinstance(next_tp, float):
                if details["action"] == "buy":
                    condition_met = current_price >= next_tp
                else:
                    condition_met = current_price <= next_tp
            else:
                # If TP is "open" or any other non-numeric marker, skip monitoring.
                condition_met = False

            if not condition_met:
                continue

            # Retrieve current position details.
            position = None
            for pos in mt5.positions_get():
                if pos.ticket == ticket:
                    position = pos
                    break
            if position is None:
                # Position may have been closed already.
                pending_trade_management.pop(ticket, None)
                continue

            # Determine the appropriate action based on the number of TP hits so far.
            tp_hit_count = details["tp_hit_count"]

            if tp_hit_count == 0:
                # First TP hit: partial close of 50% of original volume.
                partial_volume = details["lot_size"] * 0.5
                remaining_volume = position.volume
                if partial_volume > remaining_volume:
                    partial_volume = remaining_volume

                order_type = mt5.ORDER_TYPE_SELL if details["action"] == "buy" else mt5.ORDER_TYPE_BUY
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": ticket,
                    "symbol": symbol,
                    "volume": partial_volume,
                    "type": order_type,
                    "price": tick.bid if details["action"] == "buy" else tick.ask,
                    "deviation": 10,
                    "magic": 123456,
                    "comment": "Partial close at first TP",
                    "type_filling": mt5.ORDER_FILLING_IOC,
                    "type_time": mt5.ORDER_TIME_GTC,
                }
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    bot.send_message(chat_id=CHAT_ID, text=f"First TP hit for ticket {ticket}: Partial close of {partial_volume} lots executed at {current_price}.")
                    details["tp_hit_count"] = 1
                    details["closed_volume"] += partial_volume
                    details["tp_levels"].pop(0)
                else:
                    bot.send_message(chat_id=CHAT_ID, text=f"Failed partial close at first TP for ticket {ticket}. Error: {result.comment}")

            elif tp_hit_count == 1:
                # Second TP hit: set breakeven (SL = entry) for the remaining position.
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": ticket,
                    "sl": details["entry"],
                    "tp": 0.0,
                }
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    bot.send_message(chat_id=CHAT_ID, text=f"Second TP hit for ticket {ticket}: Breakeven set (SL adjusted to entry price).")
                    details["tp_hit_count"] = 2
                    details["breakeven_set"] = True
                    details["tp_levels"].pop(0)
                else:
                    bot.send_message(chat_id=CHAT_ID, text=f"Failed to set breakeven for ticket {ticket}. Error: {result.comment}")

            else:
                # Subsequent TP(s): execute further partial closes of 25% of original volume.
                partial_volume = details["lot_size"] * 0.25
                remaining_volume = position.volume
                if partial_volume > remaining_volume:
                    partial_volume = remaining_volume

                order_type = mt5.ORDER_TYPE_SELL if details["action"] == "buy" else mt5.ORDER_TYPE_BUY
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": ticket,
                    "symbol": symbol,
                    "volume": partial_volume,
                    "type": order_type,
                    "price": tick.bid if details["action"] == "buy" else tick.ask,
                    "deviation": 10,
                    "magic": 123456,
                    "comment": "Partial close at subsequent TP",
                    "type_filling": mt5.ORDER_FILLING_IOC,
                    "type_time": mt5.ORDER_TIME_GTC,
                }
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    bot.send_message(chat_id=CHAT_ID, text=f"Subsequent TP hit for ticket {ticket}: Partial close of {partial_volume} lots executed at {current_price}.")
                    details["tp_hit_count"] += 1
                    details["closed_volume"] += partial_volume
                    details["tp_levels"].pop(0)
                    # If the remaining volume is negligible, remove the trade from management.
                    if remaining_volume - partial_volume < 0.01:
                        bot.send_message(chat_id=CHAT_ID, text=f"Trade {ticket} is fully closed.")
                        pending_trade_management.pop(ticket)
                else:
                    bot.send_message(chat_id=CHAT_ID, text=f"Failed partial close at subsequent TP for ticket {ticket}. Error: {result.comment}")
        time.sleep(5)


# Start the monitoring thread.
trade_monitor_thread = threading.Thread(target=monitor_trade_signals, daemon=True)
trade_monitor_thread.start()

# ---------------------------
# Start Telegram Bot Polling
# ---------------------------
updater.start_polling()
