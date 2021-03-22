# Reference; https://www.binance.com/en/support/faq/f4c453bab89648beb722aa26634120c3

# Imports
from pprint import pprint
from functions import send_public_request, send_signed_request, BASE_URL
from datetime import datetime

if __name__ == "__main__":

    def ping_server():
        return send_public_request('/fapi/v1/ping')

    def price_data_last24hr(symbol, interval):
        klines = send_public_request(
            '/fapi/v1/klines',
            {
                'symbol' : symbol,
                'interval' : interval
            }
        )
        return klines
    
    def mark_price(symbol):
        mark_price = send_public_request(
            '/fapi/v1/premiumIndex',
            {
                'symbol' : symbol
            }
        )
        return mark_price

    def make_grid(min_price, max_price, grids):
        diff = max_price - min_price
        price_step = diff / grids

        price_list = []
        price = 0

        for i in range(0, grids):
            price = min_price + (price_step * i)
            price_list.append(price)
        
        price_list.append(max_price)

        return price_list

    def exchange_info():
        return send_public_request('/fapi/v1/exchangeInfo')

    print('\nStarting Grid Trading Bot v1.00')

    if BASE_URL == "https://fapi.binance.com":
        print('\nPing Binance USDⓈ-M Futures ...')
    else:
        print('\nPing Testnet Binance Future ...')

    # Const
    SYMBOL = 'BTCUSDT' # Choose symbol
    INTERVAL = '5m'
    MARGIN_MODE = None # Select CROSS or ISOLATED
    LEVERAGE = None # Leverage should be < 20
    GRID_COUNT = 5

    if str(ping_server()) == '{'+'}':
        print('Ping successful')

        print('\nRequesting candlesticks ...')
        candlesticks = price_data_last24hr(
            symbol=SYMBOL,
            interval=INTERVAL
        )
        # pprint(candlesticks[0])

        candlesticks = candlesticks[-289:] # 288 times 5 minutes in 24 hours

        highs, lows = [], []

        for candlestick in candlesticks:
            lows.append(float(candlestick[3]))
            highs.append(float(candlestick[4]))
        
        grid_higher_limit = max(highs)
        grid_lower_limit = min(lows)

        print(
            'Timeframe info:\n', # Display data timestamps
            'Start time:    {}\n'.format(datetime.fromtimestamp(
                candlesticks[0][0] / 1000
            )),
            'End time:      {}\n'.format(datetime.fromtimestamp(
                candlesticks[-1][0] / 1000
            ))
        )
        print(
            'Price info:\n', # Display price info
            'Max price:     {}\n'.format(grid_higher_limit),
            'Min price:     {}\n'.format(grid_lower_limit),
            'Mark price:    {}\n'.format(
                mark_price(SYMBOL)['markPrice']
            )
        )

        # Checking filters, tick_size for symbol ...
        print('\nGathering symbol filters ...')
        exchange_info = exchange_info()
        for field in exchange_info:
            if field == 'symbols':
                for symbol_info in exchange_info['symbols']:
                    if symbol_info['symbol'] == SYMBOL:
                        # pprint(symbol_info)
                        tick_size = float(symbol_info['filters'][0]['tickSize'])
                        # print(tick_size)

        # Arithmetic grid
        print('\nSetting up grid ...')
        if (grid_higher_limit - grid_lower_limit) / (GRID_COUNT + 1) < tick_size:
            print('Error: too many grids compared to tickSize: {}'.format(tick_size))

        price_points = make_grid(
            min_price=grid_lower_limit,
            max_price=grid_higher_limit,
            grids=GRID_COUNT # grids + 1 will be equal to the amount of limit orders created
        )
        print('Grid: {}\n'.format(price_points))

    else:
        print('Not successful')
