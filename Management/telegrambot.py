import MetaTrader5 as mt5
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ApplicationBuilder
import pandas as pd
import asyncio
from datetime import datetime
import threading

# ...
# CRED

Bot_username = "@TradeAlertme1"
ChatId = 803510108
from config import TOKEN, ChatId

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = TOKEN
CHAT_ID = ChatId

# Connect to MetaTrader 5
if not mt5.initialize():
    print("Failed to initialize MT5")
    quit()

class TradingBot:
    def __init__(self):
        self.application = None
        self.previous_orders = set()
        self.is_running = True
        self.monitor_task = None

    async def send_trade_alert(self, message: str):
        """Send trade alerts to the specified chat"""
        if self.application and self.application.bot:
            try:
                await self.application.bot.send_message(chat_id=CHAT_ID, text=message)
            except Exception as e:
                print(f"Error sending alert: {e}")

    async def monitor_trades(self):
        """Monitor trades asynchronously"""
        print("Trade monitoring started...")
        while self.is_running:
            try:
                orders = mt5.positions_get()
                if orders:
                    for order in orders:
                        order_id = order.ticket
                        if order_id not in self.previous_orders:
                            msg = (
                                f"New Trade Alert!\n"
                                f"Symbol: {order.symbol}\n"
                                f"Volume: {order.volume}\n"
                                f"Type: {order.type}\n"
                                f"Price: {order.price_open}"
                            )
                            await self.send_trade_alert(msg)
                            self.previous_orders.add(order_id)
            except Exception as e:
                print(f"Error in monitor_trades: {e}")
            await asyncio.sleep(10)  # Check every 10 seconds

    async def current_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command handler to show current trades"""
        try:
            orders = mt5.positions_get()
            if orders:
                msg = "Current Open Trades:\n"
                for order in orders:
                    msg += (
                        f"{order.symbol} - {order.volume} lots - "
                        f"Open Price: {order.price_open} - profit:{order.profit}- "
                        f"Stop Loss: {order.sl} - Take Profit: {order.tp}\n\n"
                    )
            else:
                msg = "No open trades."
            await update.message.reply_text(msg)
        except Exception as e:
            await update.message.reply_text(f"Error fetching trades: {str(e)}")

    async def trade_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command handler to show trade history"""
        try:
            history = mt5.history_deals_get()
            if history:
                df = pd.DataFrame(list(history), columns=["ticket", "symbol", "volume", "price", "profit"])
                msg = df.to_string(index=False)
            else:
                msg = "No trade history available."
            await update.message.reply_text(f"Trade History:\n{msg}")
        except Exception as e:
            await update.message.reply_text(f"Error fetching history: {str(e)}")

    async def close_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command handler to close a specific trade"""
        try:
            if len(context.args) != 1:
                await update.message.reply_text("Usage: /close_trade <order_id>")
                return

            order_id = int(context.args[0])
            position = None
            for pos in mt5.positions_get():
                if pos.ticket == order_id:
                    position = pos
                    break

            if position is None:
                await update.message.reply_text(f"Trade with ID {order_id} not found.")
                return

            order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

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
                await update.message.reply_text(f"Trade {order_id} closed successfully.")
            else:
                await update.message.reply_text(f"Failed to close trade {order_id}.\nError: {result.comment}")

        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for the /start command"""
        await update.message.reply_text(
            "Trading Bot is running!\n\n"
            "Available commands:\n"
            "/current_trades - Show open trades\n"
            "/trade_history - Show trade history\n"
            "/close_trade <order_id> - Close a specific trade"
        )

    async def start_monitoring(self):
        """Start the monitoring task"""
        self.monitor_task = asyncio.create_task(self.monitor_trades())
         
    def run(self):
        """Run the bot"""
        try:
            # Initialize the application
            self.application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("current_trades", self.current_trades))
            self.application.add_handler(CommandHandler("trade_history", self.trade_history))
            self.application.add_handler(CommandHandler("close_trade", self.close_trade))

            # Start monitoring trades
            # self.monitor_task = self.application.create_task(self.monitor_trades())
            # Run the TradingBot.monitor_trades coroutine
             # Start monitoring trades alongside the bot
            self.application.job_queue.run_once(callback=lambda context: asyncio.create_task(self.monitor_trades()), when=0)

            print("Bot started with trade monitoring. Press Ctrl+C to stop.")
            
           

            print("Bot started. Press Ctrl+C to stop.")
            
            # Start the bot
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            print(f"Error starting bot: {e}")
        finally:
            self.is_running = False
            if mt5.initialize():
                mt5.shutdown()

def main():
    """Main function to run the bot"""
    try:
        bot = TradingBot()
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        if mt5.initialize():
            mt5.shutdown()



            
if __name__ == '__main__':
    main()
  