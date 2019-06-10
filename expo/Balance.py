import requests
import json

def getApi():

    return 'DAR-eeTsQ1tZoAfK'

def getBalance():

    balance = '0.0000'
    url = 'https://api.aramba.ru/balance?apiKey='+getApi()
    data = ({"Language": "ru"})
    res = requests.get(url, json=data)

    if res.status_code == 200:
        balance = res.text

    print("Баланс: " + str(balance))
    return balance

def sendMessage(phone, text):

    formData = {}
    headers  = {}

    formData['SenderId']                = 'VSEEXPO'
    formData['UseRecepientTimeZone']    = False
    formData['PhoneNumber']             = phone #'89219563264'
    formData['Text']                    = text
    formData['SendDateTime']            = None
    formData['apiKey'] = getApi()

    headers['Content-Type']     = 'application/json'
    headers['Accept']           = 'application/json'
    headers['Authorization']    = getApi()

    url = 'https://api.aramba.ru/singleSms'
    res = requests.post(url, data=json.dumps(formData), headers=headers)

    print('ОТПРАВКА СЕТЬ')

    print(res.status_code)
    print(res.text)

    return True