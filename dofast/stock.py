import re
import requests
import sys
import os
from termcolor import colored
from typing import Dict, Sequence, List


# Leetcode related urls
class UrlEnum:
    MSG: str = "https://messagecenterwg.18.cn/api/MessageCenter/GetMessageMain"
    SINASH: str = "http://hq.sinajs.cn/list=sh"  # ShangHai
    SINASZ: str = "http://hq.sinajs.cn/list=sz"  # ShenZhen


class Stock():
    def __init__(self):
        self.s = requests.Session()

    def _query_message(self):
        json_dict: Dict = {
            "FMd5": "9.0.3",
            "HWareInfo": "E7C318A1-249C-4647-AE20-8BB61D1CA3E9",
            "accessToken": "2a65cce6d308495c83347c31e71c9ea7",
            "cno": -1,
            "count": 10,
            "ctype": 1,
            "ucid": "",
            "zjzh": "540750027842"
        }
        ret = self.s.post(UrlEnum.MSG, data=json_dict, verify=False)
        for r in ret.json()['Result']:
            print(r['Time'], r['Ccontent'])

    def trend(self, sid: str):
        print(sid)
        print('-' * 66)
        url = UrlEnum.SINASZ if sid.startswith(('0', '1')) else UrlEnum.SINASH
        r = re.findall(r'"(.*)"', requests.get(url + sid).text)[0].split(',')
        """ Variable shortcuts
        top: today's open price
        pcp: previous close price
        cp: current price
        thp: today's highest price
        tlp: today's lowest price
        dc: deal count (today, unit: 100)
        dv: deal value (today, unit: 10000 CNY)
        """
        date, time = r[-3], r[-2]
        name, top, pcp, cp, thp, tlp = r[:6]
        dc, dv = int(r[8]) // 100, int(float(r[9])) / 1000000
        top5buyers, top5sellers = r[10:20], r[20:30]

        def calculate_ratio(r: float,
                            s: float) -> str:  # r calculated agains s
            x = float(r) / float(s) - 1
            return colored(str(round(x *
                                     100, 4)), 'green') if x < 0 else colored(
                                         '+' + str(round(x * 100, 4)), 'red')

        print("{:<25}: {:<15}".format("Time", date + " / " + time))
        print("{:<25}: {:<15}".format("Stock name", name))
        print("{:<25}: {}".format("Previous close price", pcp))
        print("{:<25}: {} ({}%)".format("Today open price", top,
                                        calculate_ratio(top, pcp)))
        print("{:<25}: {} ({}%) 👈 ".format("Current price", cp,
                                           calculate_ratio(cp, pcp)))
        print("{:<25}: {} ({}%)".format("Today highest price", thp,
                                        calculate_ratio(thp, pcp)))
        print("{:<25}: {} ({}%)".format("Today lowest price", tlp,
                                        calculate_ratio(tlp, pcp)))
        # print('-'*66)

        top, tlp, thp = float(top), float(tlp), float(thp)
        print("{:<25}: {:<2.3f} ".format("Suggested ASK price",
                                         round(thp * 0.1 + tlp * 0.9, 3)))
        print("{:<25}: {:<2.3f} ".format("Suggested BID price",
                                         round(tlp * 0.1 + thp * 0.9, 3)))

        return
        print("{:<25}: {} (rl = 100 shares)".format("Deal count", dc))
        print("{:<25}: {} (Millions)".format("Deal value", dv))
        print("Top five asks: ")
        for i in range(0, 10, 2):
            print("{:>25} {:<10}".format(top5buyers[i + 1],
                                         int(top5buyers[i]) // 100))

        print("Top five bids: ")
        for i in range(0, 10, 2):
            print("{:>25} {:<10}".format(top5sellers[i + 1],
                                         int(top5sellers[i]) // 100))

    def my_trend(self):
        self.trend('002563')
        self.trend('600429')


if __name__ == "__main__":
    Stock().trend('600429')
    Stock().trend('002563')
