
import yfinance as yf
from apscheduler.schedulers.blocking import BlockingScheduler
from email.message import EmailMessage
import ssl
import smtplib

from dotenv import load_dotenv
import os
load_dotenv()


def get_data(symbol="AAPL"):
    #define the ticker symbol
    ticker_symbol = symbol
    #create the ticker object
    tickerObject = yf.Ticker(ticker_symbol)
    #get the historical prices for this ticker
    return tickerObject.history(period="1d", interval="30m")




gmail_user = os.getenv('EMAIL_ADDRRESS')
gmail_password = os.getenv('EMAIL_PASSWORD')

em = EmailMessage()

gmail_user = gmail_user
gmail_password = gmail_password
subject = 'info signal'



def test_engulfing(df):
    last_open = df.iloc[-1, :].Open
    last_close = df.iloc[-1, :].Close
    previous_open = df.iloc[-2, :].Open
    previous_close = df.iloc[-2, :].Close

    if (previous_open < previous_close #BULLISH TREND    CONDITION
        and last_open > previous_close 
        and last_close < previous_open):
        return 1  # Bearish Engulfing Pattern
    
    elif (previous_open > previous_close #bEARISH TREND
          and last_open < previous_close 
          and last_close > previous_open):
        return 2  # Bullish Engulfing Pattern
    else:
        return 0  # No Engulfing Pattern








symbols =  ['AAPL', 'NVDA', 'PYPL', 'GOOG', 'MSFT', 'AMZN']

def some_job():
    msg="Trading Signal Message \n"
    for symb in symbols:
        historical_data = get_data(symb)
        if test_engulfing(historical_data)==1:
            msg = msg + str(symb+": the signal is 1 bearish") + "\n"

        elif test_engulfing(historical_data)==2:
            msg = msg + str(symb+": the signal is 2 bullish") + "\n"
    
    em['From'] = gmail_user
    em['To'] = gmail_user
    em['Subject'] = subject
    em.set_content(msg)

    context = ssl.create_default_context()

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(gmail_user, gmail_user, em.as_string())
    server.close()

#some_job()

# Define the UTC timezone
# utc = pytz.utc

import pytz

# Define the EST timezone
est = pytz.timezone('US/Eastern')

###################################################################
## Interval time job ##############################################
scheduler = BlockingScheduler(job_defaults={'misfire_grace_time': 60*60}) # 1 hour = 60*60 for misfire
scheduler.add_job(some_job, 'cron', day_of_week='mon-fri', hour=0, minute=0, timezone=est)
scheduler.start()