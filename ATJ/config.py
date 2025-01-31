

from dotenv import load_dotenv
import os

load_dotenv()       
login = os.getenv('login2')
password = os.getenv('password2')
server = os.getenv('server2')


mt5_credentials = {
    'login': login,
    'password': password,
    'server': server,
    'exe_path': None
}

login2 = 192918303
password2 = 'Demo@1234'
server2 = 'Exness-MT5Trial'

def initialize_mt5():
    import MetaTrader5 as mt5
    mt5.initialize()

    # mt5.initialize(mt5_credentials['exe_path'])
    # mt5.login(mt5_credentials['login'], mt5_credentials['password'], mt5_credentials['server'])
    # print(mt5.account_info())
    # print(mt5_credentials)
    
    if not mt5.login(login2, password2, server2):
        print("Failed to connect to the server")
    else:
        print("Connected to the server successfully")
        print(mt5.account_info())
    
    return mt5

# initialize_mt5()

if __name__ == '__main__':
    initialize_mt5()
    
    