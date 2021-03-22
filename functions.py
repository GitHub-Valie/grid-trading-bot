# Imports
import hmac, hashlib, time, json, requests, os
from os.path import join, dirname
from urllib.parse import urlencode
from dotenv import load_dotenv

# Environment variables: Binance API keys
production = False

# Binance Future
if production == True:
    load_dotenv(join(dirname(__file__), '.env'))
    API_KEY = os.environ.get('API_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BASE_URL = "https://fapi.binance.com"
else:
    load_dotenv(join(dirname(__file__), '.env'))
    API_KEY = os.environ.get('TEST_API')
    SECRET_KEY = os.environ.get('TEST_SECRET')
    BASE_URL = "https://testnet.binancefuture.com"

# https://binance-docs.github.io/apidocs/spot/en/#endpoint-security-type
def hashing(query_string):
    '''
    Converts a ```query_string``` into an integer known as a hash of that ```query_string```.
    '''
    return hmac.new(
        SECRET_KEY.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def get_timestamp():
    '''
    Returns the timestamp for the current time
    '''
    return int(time.time() * 1000)

def dispatch_request(http_method):
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json;charset=utf-8',
        'X-MBX-APIKEY': API_KEY
    })
    return {
        'GET': session.get,
        'DELETE': session.delete,
        'PUT': session.put,
        'POST': session.post
    }.get(http_method, 'GET')

def send_signed_request(http_method, url_path, payload={}):
    '''
    Used for endpoints that require a valid API-Key and signature: ```TRADE```, ```MARGIN```
    , ```USER_DATA```
    '''
    query_string = urlencode(payload)
    query_string = query_string.replace('%27', '%22')
    if query_string:
        query_string = "{}&timestamp={}".format(
            query_string,
            get_timestamp()
        )
    else:
        query_string = 'timestamp={}'.format(get_timestamp())
    
    url = BASE_URL + url_path + '?' + query_string + '&signature=' + hashing(query_string)
    # print('{} {}'.format(
    #     http_method,
    #     url
    # ))
    params = {
        'url' : url,
        'params' : {}
    }
    response = dispatch_request(http_method)(**params)
    return response.json()

def send_public_request(url_path, payload={}):
    '''
    Used for endpoints that don't require a signature: ```NONE```, ```USER_STREAM```, 
    ```MARKET_DATA```
    '''
    query_string = urlencode(payload, True)
    url = BASE_URL + url_path
    if query_string:
        url = url + '?' + query_string
    # print("{}".format(
    #     url
    # ))
    response = dispatch_request('GET')(url=url)
    return response.json()