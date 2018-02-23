# coding:utf-8
__author__ = "dfk"
__date__ = "2018/2/19 10:57"

import requests
import json


class YunPian(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.singal_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self, code, mobile):
        parmas = {
            "api_key": self.api_key,
            "mobile": mobile,
            "text": "xxxxx{code}".format(code=code)
        }
        response = requests.post(self.singal_send_url, data=parmas)
        re_dict = json.loads(response.text)
        print(re_dict)


if __name__ == "__main__":
    yunpian = YunPian('sdfadfasfa')
    yunpian.send_sms('2017', 'your mobile')
