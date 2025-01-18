import MetaTrader5 as mt5
from time import sleep





if __name__ == '__main__':
    mt5.initialize()
    
    
    
    
    
    while True:
        print(mt5.positions_get(symbol='EURUSD'))
        sleep(1)