

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


def initialize_mt5():
    import MetaTrader5 as mt5

    mt5.initialize(mt5_credentials['exe_path'])
    mt5.login(mt5_credentials['login'], mt5_credentials['password'], mt5_credentials['server'])
    print(mt5.account_info())
    return mt5.initialize()
    
    
# Automatically connect to MetaTrader when the config.py file is imported
initialize_mt5()    