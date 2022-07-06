import requests
import json
from error_logger import *
from datetime import date, timedelta
from colorama import Fore, Style


def check_request(r: object) -> object or None:
    '''
    Function checks the header of the request and, in case of an error, sends the data to be written to the logs
    @return: r - object of request
    '''
    if r.status_code == 200:
        return r
    elif r.status_code < 300:
        error_log(r)
        return r
    else:
        print(f'{str(r.status_code)}: {str(r.text)}')
        error_log(r)


def get_available_curr(url_curr: str, params: dict) -> list or None:
    '''
    Function gets the list of current currency symbols that can be converted

    @param: url_curr - api link to active currencies
    @param: params - dictionary of settings necessary for api

    @return: list of available currencies or if API don't response properly, quit program.
    '''
    try:
        r = requests.get(url=url_curr, params=params)
        r = check_request(r)
        result_data = json.loads(r.text)
    except Exception as e:
        error_log(e)
        print('Internet connection problem. Check error log.')
        quit()

    available_curr_symbols = []
    for key in result_data['results']:
        available_curr_symbols.append(key)

    return available_curr_symbols


def get_exchange_rate(symbols: list, url: str, api_key) -> list:
    '''
    Function gets the current conversion rate

    @param: symbols - list of correct currencies symbols
    @param: url - string api url
    @param: api_key - dictionary of necessary data for api request

    @return: list of acquired data
    '''
    symbols = symbols[:2]
    currency_pair = '_'.join(symbols)

    today = date.today()
    today = today.strftime('%Y-%m-%d')

    yesterday = date.today() - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    params = {
        'apiKey': api_key,
        'q': currency_pair,
        'compact': 'ultra',
        'date': yesterday,
        'endDate': today
    }

    try:
        r_today_yesterday = requests.get(url, params=params)
        r_today_yesterday = check_request(r_today_yesterday)
        curr_pairs_dict = json.loads(r_today_yesterday.text)
    except Exception as e:
        error_log(e)
        quit()

    for key in curr_pairs_dict:
        data_yesterday = curr_pairs_dict[key][yesterday]
        data_today = curr_pairs_dict[key][today]

        if data_today > data_yesterday:
            output = [data_today, '+', f'{Fore.GREEN}%.2f{Style.RESET_ALL}' % data_today]
            return output

        elif data_today < data_yesterday:
            output = [data_today, '-', f'{Fore.RED}%.2f{Style.RESET_ALL}' % data_today]
            return output

        else:
            return [data_today, '*', f'{Fore.WHITE}%.2f{Style.RESET_ALL}' % data_today]
