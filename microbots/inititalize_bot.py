import MetaTrader5 as mt5

# login = 5032468329
# password = "Z*EeWsZ4"
# server = "MetaQuotes-Demo"

login = 192918303
password = "Demo@1234"
server = "Exness-MT5Trial"

def initialize_bot():
    # connect to MetaTrader5 Terminal
    isconennected= mt5.initialize()
    if not isconennected:
        print("initialize() failed")
        mt5.shutdown()
        quit()
    # login to your Trading Account 
   
    
    if not mt5.login(login, password, server):
        print("Failed to connect to the server")
    else:
        print("Connected to the server successfully")
        print(mt5.account_info())
    


# mt5.login(login, password, server)


