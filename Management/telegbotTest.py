from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# CRED

TOKEN ="7078638445:AAH3OF4Usyiq6KPo46dtzdcvwA4US-ZJLJY"
Bot_username = "@TradeAlertme1"
ChaId2 = 803510108
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    await update.message.reply_text(f'Hello dear {update.effective_user.first_name}')

async def welcome_user(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    
    await update.message.reply_text(f'Welcome to the Test bot')

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("Hello", hello))
app.add_handler(CommandHandler("Welcome", welcome_user))
app.run_polling()

