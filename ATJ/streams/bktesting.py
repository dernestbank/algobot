# # for python scripts
# import sys
# from os.path import dirname, abspath
# d = dirname(dirname(abspath(__file__)))
# print('d :', d)
# sys.path.append(d)
# # sys.path.append('../..')
# from backtester_simulator.backtest_simulator import create_app


# app=create_app('ATJ\streams\bollinger_backest.json', num_candles=100, candle_step=1, 
#             #    strategy_name='Strategy'
#                )

# if __name__ == '__main__':
#     app.run()


import sys
from os.path import dirname, abspath, join

try:
    # Get the root directory (algobot)
    root_dir = dirname(dirname(dirname(abspath(__file__))))
    
    # Add the ATJ directory to Python path
    atj_path = join(root_dir, 'ATJ')
    sys.path.append(atj_path)
    
    print('Python paths:')
    print(f'Root directory: {root_dir}')
    print(f'ATJ directory: {atj_path}')
    
    # Now import should work
    from backtester_simulator.backtest_simulator import create_app

    app = create_app(r'C:\Users\derne\OneDrive - The Pennsylvania State University\Programming\Extra\algobot\ATJ\streams\bollinger_backtest.json', 
                     num_candles=100, 
                     candle_step=1)

    if __name__ == '__main__':
        app.run()
        
except Exception as e:
    print(f"Error occurred: {str(e)}")
    print(f"Current directory: {abspath('.')}")
    print(f"Python path: {sys.path}")
    raise