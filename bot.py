#SoloBot
import requests, time
from config import *

###### Exchange API ######
def get_rates():
    r = requests.get(CURRENCIES_BASE_URL)
    return r.json()

def get_base_rates(currency):
    r = requests.get(CURRENCIES_BASE_URL + '?base=' + currency)
    return r.json()

def get_currencies_list():
    return list(get_rates()['rates'].keys())

def get_currency(currency):
    return get_rates()['rates'][currency]

def get_base_currency(currency):
    return get_base_rates(currency)['rates']['EUR']


###### Bot logic ######
global recent_update_id
global currency
recent_update_id = 0
currency = None

def if_currency(currency):
    if currency:
        return True
    else:
        return False

def select_currency(chat_id):
    send_message(chat_id, 'Select your currency from the list: ' + ', '.join(get_currencies_list()))

def get_updates():
    url = URL + 'getupdates?offset=' + str(recent_update_id)
    r = requests.get(url)
    return r.json()

def get_message():
    data = get_updates()
    last_object = data['result'][-1]
    current_update_id = last_object['update_id']

    global recent_update_id
    if recent_update_id != current_update_id:
        recent_update_id = current_update_id
        chat_id = last_object['message']['chat']['id']
        message_text = last_object['message']['text']
        message = {'chat_id': chat_id,
                   'text': message_text}
        return message
    return None

def send_message(chat_id, text):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    requests.get(url)

def main():
    while True:
        answer = get_message()
        if answer:
            chat_id = answer['chat_id']
            text = answer['text'].split()
            global currency
            if text[0] == '/start' or text[0] == '/help':
                send_message(chat_id, 'Hello, I\'m your EuroAccountant, I was born to calculate currencies to Euro and back.' +\
                    '\nAll you need is to set your native currency then use simple commands:' +\
                    '\nFor example:' +\
                    '\n"HUF" - I will set Hungarian forint as your native currency' +\
                    '\n"10 HUF" - I will count 10 Hungarian forintes to Euro' +\
                    '\n"10" - I will count 10 Euro to Hungarian forintes')
                select_currency(chat_id)
            elif text[0] == '/mycurrency':
                if if_currency(currency):
                    send_message(chat_id, 'Current currency is ' + currency)
                else:
                    select_currency(chat_id)
            elif text[0].upper() in get_currencies_list():
                currency = text[0].upper()
                send_message(chat_id, 'Selected currency is ' + currency)
            elif text[0].isdigit():
                if if_currency(currency):
                    if len(text) > 1:
                        if text[1].upper() == currency:
                            send_message(chat_id, text[0] + ' ' + text[1].upper() + ' is ' + str(float(text[0]) * round(float(get_base_currency(currency)), 2)) + ' Euro')
                    else:
                        send_message(chat_id, text[0] + ' Euro is ' + str(float(text[0]) * round(float(get_currency(currency)), 2)) + ' ' + currency)
                else:
                    select_currency(chat_id)
        time.sleep(1)

if __name__ == '__main__':
    main()
