# Imports
from pprint import pprint
from functions import send_public_request, send_signed_request
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

    def make_grid(min_price, max_price, steps):
        diff = max_price - min_price
        price_step = diff / steps

        price_list = []
        price = 0

        for i in range(0, steps):
            price = min_price + (price_step * i)
            price_list.append(price)
        
        price_list.append(max_price)

        return price_list

    if str(ping_server()) == '{'+'}':
        print('\nPing successful')

        print('\nRequesting price data ...')
        candlesticks = price_data_last24hr(
            symbol='BTCUSDT',
            interval='5m'
        )

        # pprint(candlesticks[0])

        candlesticks = candlesticks[-288:] # 288 times 5 minutes in 24 hours

        highs, lows = [], []

        for candlestick in candlesticks:
            lows.append(float(candlestick[3]))
            highs.append(float(candlestick[4]))
        
        max_price = max(highs)
        min_price = min(lows)

        # Display data timestamps
        print('Start time:  ', datetime.fromtimestamp(candlesticks[0][0] / 1000))
        print('End time:    ', datetime.fromtimestamp(candlesticks[-1][0] / 1000))

        print('Max price:   ', max_price)
        print('Min price:   ', min_price)
        print('Mark price:  ', mark_price('BTCUSDT')['markPrice'])
        print('Spread:      ', max_price - min_price)

        print('\nSetting up grid ...')

        # Arithmetic grid
        price_grid = make_grid(
            min_price=min_price,
            max_price=max_price,
            steps=5
        )
        print('Grid: ', price_grid)

    else:
        print('Not successful')
