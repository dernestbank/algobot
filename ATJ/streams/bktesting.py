# for python scripts
import sys
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
print('d :', d)
sys.path.append(d)
# sys.path.append('../..')
from backtester_simulator.backtest_simulator import create_app


app=create_app('ATJ\streams\bollinger_backest.json', num_candles=100, candle_step=1, 
            #    strategy_name='Strategy'
               )

if __name__ == '__main__':
    app.run()
