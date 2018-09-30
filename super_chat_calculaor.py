#!/usr/bin/env python3
# -*- encoding: utf-8

'''
Author: Siqi Deng, deng47@gmail.com
Version: 1.0 09/30/2018
'''


import requests
import re
import json

def str_to_money(str):
    str = str.replace(',','')
    currency = re.findall('(.*?)\d+',str)[0]
    amount = float(re.findall('\d+',str)[0])
    return {currency:amount}

video_link = input("video_link: ")
#video_link = "https://www.youtube.com/watch?v=IQYgcfEKOMQ"

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
html = session.get(video_link, headers=headers).text
basic_link = "https://www.youtube.com/live_chat_replay/get_live_chat_replay?continuation="
continuation = re.findall('"continuation":"(.*?)"', html)[-1]
next_link = basic_link + continuation + '&hidden=false&pbj=1'

all = {}
currencies = {}

while continuation:
    html = session.get(next_link, headers=headers).text
    try:
        for each in json.loads(html)['response']["continuationContents"]["liveChatContinuation"]["actions"]:
            if "addChatItemAction" in each["replayChatItemAction"]["actions"][0] and 'liveChatPaidMessageRenderer' in  each["replayChatItemAction"]["actions"][0]["addChatItemAction"]['item']:
                raw_info = each["replayChatItemAction"]["actions"][0]["addChatItemAction"]['item']['liveChatPaidMessageRenderer']

                supporter = raw_info['authorName']['simpleText']
                amount = raw_info['purchaseAmountText']['simpleText']
                print(supporter, amount)
                money = str_to_money(amount)
                currency = [key for key in money.keys()][0]
                if currency not in currencies:
                    currencies.update(money)
                else:
                    currencies[currency] += money[currency]
                if supporter not in all:
                    all[supporter] = money
                else:
                    all[supporter][currency] += money[currency]
                        

        continuation = json.loads(html)['response']["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]


        next_link = basic_link + continuation + '&hidden=false&pbj=1'
    except:
        break

#print(all)
print(currencies)


