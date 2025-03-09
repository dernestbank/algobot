import MetaTrader5 as mt5
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import pandas as pd
import time

# CRED

TOKEN ="7078638445:AAH3OF4Usyiq6KPo46dtzdcvwA4US-ZJLJY"
Bot_username = "@TradeAlertme1"
ChatId = 803510108

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = TOKEN
CHAT_ID = ChatId

# Connect to MetaTrader 5
if not mt5.initialize():
    print("Failed to initialize MT5")
    quit()
    
# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

############################################
#          Functions 
###########################################
# Function to send trade alerts
def send_trade_alert(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

# Function to check for new trades
def monitor_trades():
    previous_orders = set()
    while True:
        orders = mt5.positions_get()
        if orders:
            for order in orders:
                order_id = order.ticket
                if order_id not in previous_orders:
                    msg = f"New Trade Alert!\nSymbol: {order.symbol}\nVolume: {order.volume}\nType: {order.type}\nPrice: {order.price_open}"
                    send_trade_alert(msg)
                    previous_orders.add(order_id)
        time.sleep(10)  # Check every 10 seconds
    
# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Function to send trade alerts
def send_trade_alert(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

# Function to check for new trades
def monitor_trades():
    previous_orders = set()
    while True:
        orders = mt5.positions_get()
        if orders:
            for order in orders:
                order_id = order.ticket
                if order_id not in previous_orders:
                    msg = f"New Trade Alert!\nSymbol: {order.symbol}\nVolume: {order.volume}\nType: {order.type}\nPrice: {order.price_open}"
                    send_trade_alert(msg)
                    previous_orders.add(order_id)
        time.sleep(10)  # Check every 10 seconds

# Command to show current trades
def current_trades(update: Update, context: CallbackContext):
    orders = mt5.positions_get()
    if orders:
        msg = "Current Open Trades:\n"
        for order in orders:
            msg += f"{order.symbol} - {order.volume} lots - Open Price: {order.price_open} - profit:{order.profit}- Stop Loss: {order.sl} - Take Profit: {order.tp}\n\n"
    else:
        msg = "No open trades."
    update.message.reply_text(msg)

# Command to show trade history
def trade_history(update: Update, context: CallbackContext):
    history = mt5.history_deals_get()
    if history:
        df = pd.DataFrame(list(history), columns=["ticket", "symbol", "volume", "price", "profit"])
        msg = df.to_string(index=False)
    else:
        msg = "No trade history available."
    update.message.reply_text(f"Trade History:\n{msg}")


    
    # Telegram Bot Command Setup
updater = Updater(TOKEN, update_queue=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("current_trades", current_trades))
dispatcher.add_handler(CommandHandler("trade_history", trade_history))

# Start the bot
updater.start_polling()

# Start monitoring trades in a separate thread
import threading
trade_monitor_thread = threading.Thread(target=monitor_trades, daemon=True)
trade_monitor_thread.start()

################################################################
#                        Extra

# Close Trades via Telegram
def close_trade(update: Update, context: CallbackContext):
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /close_trade <order_id>")
            return

        order_id = int(context.args[0])

        # Retrieve the position
        position = None
        for pos in mt5.positions_get():
            if pos.ticket == order_id:
                position = pos
                break

        if position is None:
            update.message.reply_text(f"Trade with ID {order_id} not found.")
            return

        # Determine order type (buy/sell) and reverse it to close
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

        # Close the trade
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": order_id,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "price": mt5.symbol_info_tick(position.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask,
            "deviation": 10,
            "magic": 123456,
            "comment": "Closed via Telegram Bot",
            "type_filling": mt5.ORDER_FILLING_IOC,
            "type_time": mt5.ORDER_TIME_GTC,
        }

        result = mt5.order_send(request)

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            update.message.reply_text(f"Trade {order_id} closed successfully.")
        else:
            update.message.reply_text(f"Failed to close trade {order_id}.\nError: {result.comment}")

    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

# Register the command
dispatcher.add_handler(CommandHandler("close_trade", close_trade))

