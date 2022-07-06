import os
import sys
import dbwriter
from api_functions import *
from error_logger import *
import re


class Pair:
    def __init__(self, value: str):
        self.value = value
        symbols = self.extract_symbols()
        if len(symbols) == 2 and verify_symbols(symbols, available_curr_symbols) is True:
            self.currency_a = symbols[0]
            self.currency_b = symbols[1]

        elif isinstance(symbols, str):
            print('Bad input. Allowed only input like: "ABC XYZ".')

    def __str__(self) -> str:
        '''
        The function generates a valid format for the api

        @return: valid string for api
        '''
        return f'{self.currency_a}_{self.currency_b}'

    def extract_symbols(self) -> list[str] or str:
        '''
        Method searches for a pattern match and creates a list of currency pairs to convert
        Otherwise, it returns a warning to the user about incorrect input form

        @return: list of currency symbols or warning string
        '''
        data = re.match('[\w]{3} [\w]{3}', self.value)
        if data:
            return data.group().split(' ')

        else:
            return 'Bad input. Allowed only input like: "ABC XYZ".'


def show_history() -> None:
    '''
    Function displays the user's search history
    '''
    conn = dbwriter.create_connection()
    dbwriter.open_db(conn)
    rows = dbwriter.read(conn)
    dbwriter.close_db(conn)

    # if rows == []
    if not rows:
        print('History is empty. Nothing to show. Type your first currency pair like "EUR USD"')
        return None

    else:
        for row in rows:
            for i in range(len(row[:-1])):
                if i == 3:
                    if row[-1] == '+':
                        rate = f'{Fore.GREEN}%.2f{Style.RESET_ALL}' % float(row[i])
                    elif row[-1] == '-':
                        rate = f'{Fore.RED}%.2f{Style.RESET_ALL}' % float(row[i])
                    else:
                        rate = f'{Fore.WHITE}%.2f{Style.RESET_ALL}' % float(row[i])

                    print(rate, end=' ')
                else:
                    print(row[i], end=' ')
            print('')


def verify_symbols(symbols: list, available_curr_symbols: list = None) -> bool:
    '''
    Function checks whether the inserted currency symbol is in the list of available symbols for conversion

    @param: symbols - list of inserted currency symbols
    @param: available_curr_symbols: list of available symbols for conversion

    @return: boolean
    '''
    for symbol in symbols:
        if symbol.upper() not in available_curr_symbols:
            print(f'Symbol {symbol} is not valid. Check typos...')
            return False
    return True


def get_request_time() -> dict:
    '''
    Function generates the date and time when the query was made

    @return: dictionary of dates and times
    '''
    request_time = {}
    now = datetime.now()
    request_time['timestamp'] = now.timestamp()
    request_time['date'] = now.strftime('%Y-%m-%d')
    request_time['time'] = now.strftime('%H:%M:%S')
    request_time['date_time'] = now.strftime('%Y-%m-%d %H:%M:%S')
    get_request_time.date_time = request_time['date_time']
    return request_time


def show_help() -> None:
    print('in cli')
    print('{:<25} {:<50}'.format('-h or --history', 'show history'))
    print('{:<25} {:<50}'.format('apikey:123456789', 'add / rewrite your own apikey instead apikey in env'))
    print('')
    print('in input')
    print('{:<25} {:<50}'.format('history', 'show history'))
    print('{:<25} {:<50}'.format('quit', 'quit program'))
    print('{:<25} {:<50}'.format('EUR USD', 'get current conversion rate'))

# read links and endpoints
with open('endpoints.json', 'r') as endpoints:
    links = json.load(endpoints)

    base_url = links['base_url']
    endpoint_list_of_currencies = links['endpoint_list_of_currencies']
    endpoint_compact = links['endpoint_compact']

url_curr_list = base_url + endpoint_list_of_currencies
url_curr_pair_rate = base_url + endpoint_compact

if os.getenv('my_secret_api_key') is not None:
    api_key = os.getenv('my_secret_api_key')
else:
    api_key = input('You don\'t set secret api key in to environment. Enter your api key here: ')

params = {'apiKey': api_key}
available_curr_symbols = get_available_curr(url_curr_list, params)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        help_flags = ['-h', '--help']
        if sys.argv[1] in help_flags:
            show_help()
            quit()

        elif sys.argv[1] == '--history':
            show_history()

        elif 'apikey:' in sys.argv[1]:
            # apikey:123456789 -> ['apikey', '123456789'] -> '123456789'
            api_key = sys.argv[1].split(':')[1]

    while True:
        pair_to_convert = input('Enter currency pair: ')

        if pair_to_convert == 'quit':
            print('Good bye!')
            quit()

        elif pair_to_convert == 'history':
            show_history()
            continue

        if len(pair_to_convert) != 7:
            # inject bad input for second verification round
            # without this it was work if input was 'eur usd chf'
            pair_to_convert = 'qwert qwert'
        data_for_db = get_request_time()

        pair_to_convert = Pair(pair_to_convert.upper())
        try:
            symbols = [pair_to_convert.currency_a, pair_to_convert.currency_b]
        except AttributeError:
            continue
            # it's mean, initialization failed -> incorrect input from user
            # user was informed by message on screen

        curr_rate = get_exchange_rate(symbols, url_curr_pair_rate, api_key)

        # enter the obtained data
        data_for_db['curr_convert_rate'] = curr_rate[0]
        data_for_db['change'] = curr_rate[1]
        data_for_db['pair'] = ' '.join(symbols)

        # write them to the database
        conn = dbwriter.create_connection()
        dbwriter.open_db(conn)
        dbwriter.write(conn, data_for_db)
        dbwriter.close_db(conn)

        # give the answer to user
        if isinstance(curr_rate, list):
            print(f'You must pay {curr_rate[2]} {symbols[1]} for 1 {symbols[0]}')
        else:
            print(curr_rate)
