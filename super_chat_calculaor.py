#!/usr/bin/env python3
# -*- encoding: utf-8

'''
Author: Siqi Deng, deng47@gmail.com
Version: 1.1 10/12/2018
'''


import requests
import datetime
import re
import json


def str_to_money(str):
    str = str.replace(',','')
    currency = re.findall('(.*?)\d+',str)[0]
    amount = float(re.findall('\d+',str)[0])
    return {currency:amount}


def get_live_comment_link(url):
    global session, basic_linka, lengthSeconds
    start_link = "https://www.youtube.com/live_chat_replay?continuation="
    html = session.get(url, headers=headers).text
    continuation = re.findall('"continuation":"(.*?)"', html)[2]
    lengthSeconds = int(re.findall('\"lengthSeconds\":\"(\d+)\"', html)[0])
    next_link = start_link + continuation + '&hidden=false&pbj=1'
    html = session.get(next_link, headers=headers).text
    extract_superchat(json.loads(html)[1]["response"])
    continuation = json.loads(html)[1]['response']["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]
    next_link = basic_link + continuation + '&hidden=false&pbj=1'
    return next_link


def extract_superchat(json_data):
    global last_timestamp, timestamp, last_superchat, currencies, all
    for each in json_data["continuationContents"]["liveChatContinuation"]["actions"]:
        timestamp = int(each["replayChatItemAction"]["videoOffsetTimeMsec"])
        if "addChatItemAction" in each["replayChatItemAction"]["actions"][0] and 'liveChatPaidMessageRenderer' in  each["replayChatItemAction"]["actions"][0]["addChatItemAction"]['item']:
            raw_info = each["replayChatItemAction"]["actions"][0]["addChatItemAction"]['item']['liveChatPaidMessageRenderer']

            supporter = raw_info['authorName']['simpleText']
            amount = raw_info['purchaseAmountText']['simpleText']
            time = raw_info["timestampText"]['simpleText']

            if last_timestamp <= timestamp and last_superchat != time+supporter+amount:
                last_timestamp = timestamp
                last_superchat = time+supporter+amount
                print("### FOUND ###", time, supporter, amount)
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
            else:
                print("### SKIP DUPLICATED ###", time, supporter, amount)



all = {}
currencies = {}
last_timestamp = 0
last_superchat = ""
jump_to = 0

video_link = input("video_link: ")
#video_link = "https://www.youtube.com/watch?v=aocN_6AuA-c"   # 【生誕祭LIVE】 YuNiの誕生日(10/1)をみんなで一緒に迎えよう！！の会SP
#video_link = "https://www.youtube.com/watch?v=VAGT3c2waj0"   # Sharpness Radio 【第８回】

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
html = session.get(video_link, headers=headers).text
basic_link = "https://www.youtube.com/live_chat_replay/get_live_chat_replay?continuation="
next_link = get_live_comment_link(video_link)


while True:
    html = session.get(next_link, headers=headers).text
    if "continuationContents" not in json.loads(html)['response']:
        jump_to += 1
        if (timestamp//1000)+ jump_to >= lengthSeconds:
            break
        print("### JUMP TO ###", video_link + "&t=%ss" % str((timestamp//1000)+ jump_to))
        next_link = get_live_comment_link(video_link + "&t=%ss" % str((timestamp//1000)+ jump_to))
        continue
    json_response = json.loads(html)['response']["continuationContents"]["liveChatContinuation"]
    if "liveChatReplayContinuationData" in json_response["continuations"][0]:
        continuation = json_response["continuations"][0]["liveChatReplayContinuationData"]["continuation"]
        next_link = basic_link + continuation + '&hidden=false&pbj=1'
        extract_superchat(json.loads(html)['response'])

    else:
        jump_to += 1
        if (timestamp//1000)+ jump_to >= lengthSeconds:
            break
        print("### JUMP TO ###", video_link + "&t=%ss" % str((timestamp//1000)+ jump_to))
        next_link = get_live_comment_link(video_link + "&t=%ss" % str((timestamp//1000)+ jump_to))


print(currencies)


