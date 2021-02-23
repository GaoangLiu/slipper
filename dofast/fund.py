import json
import math
import re
import requests
import time
from bs4 import BeautifulSoup

class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Fund():
    def __init__(self, fundcode='110022'):
        self.fundcode = fundcode

    def _get_headers(self):
        headers = {}
        headers[
            "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)"
        headers[
            'Referer'] = "http://fund.eastmoney.com/{}.html?spm=search".format(
                self.fundcode)
        return headers

    def get_real_price(self):
        s = requests.Session()
        rt = int(round(time.time() * 1000)).__str__()
        res = re.findall(
            r'\((.*)\)',
            s.get("http://fundgz.1234567.com.cn/js/{}.js?rt={}".format(
                self.fundcode, rt),
                  headers=self._get_headers()).text)
        if not res:
            print('Not price was found.')
            return {}
        return json.loads(res[0])

    def get_share_detail(self):
        headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers[
            'User-Agent'] = 'app-iphone-client-iPhone9,1-7974C942-FE58-47D8-AC1A-AE327BC558A4'

        params = {'FundCode': self.fundcode}

        s = requests.Session()
        res = s.post(
            'https://tradeapilvs.1234567.com.cn/User/home/GetMyAssetDetails',
            data=params,
            headers=headers)
        if res.status_code == 200:
            return json.loads(res.text)

    def printBasicInfo(self):
        rti = self.get_real_price()  # real time info
        estimated_profit_rate = 0
        if rti:
            print('{:>30} {}'.format('Name', rti['name']))
            print('{:>30} {}'.format('Code', rti['fundcode']))
            print('{:>30} {}'.format('Estimate time', rti['gztime']))
            print('{:>30} {} / {}'.format('Estimate / Pure Value', rti['gsz'],
                                          rti['dwjz']))

            e, p = float(rti['gsz']), float(rti['dwjz'])
            r = (e - p) / p * 100
            if e < p:
                _invest = round(max(1000 * math.exp(1 + 2 / r), 100 * abs(r)),
                                2)
                _ratio = round(r, 2)
                # print(_invest)
                print('{:>30} {:<5} ({:<5})'.format(
                    'You should invest',
                    bcolors.BOLD + bcolors.GREEN + str(_invest),
                    str(_ratio) + bcolors.ENDC))
            else:
                r = int(r * 100) / 100.0
                print('{:>30} {} %'.format(
                    'congrats!',
                    bcolors.RED + bcolors.BOLD + str(r) + bcolors.ENDC))

        print("\n")


def show_sz_index():
    ''' Show today's shanghai index 
    '''
    eastmoney_url = 'https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids=1.000001%2C0.399001%2C0.399006%2C1.000300%2C0.399005%2C1.000016'
    r = requests.Session().get(eastmoney_url, verify=False)
    j = r.json()
    print('-' * 70)
    for index in j['data']['diff']:
        value, diff, name = index['f2'], index['f4'], index['f14']
        color = bcolors.RED + bcolors.BOLD if diff > 0 else bcolors.GREEN + bcolors.BOLD
        ratio = float(diff) * 100 / (float(value) - float(diff))
        colored_diff = color + str(diff) + bcolors.ENDC
        colored_diff += (20 - len(colored_diff)) * ' '
        print("{:<12} {:<10} {:<20} {:2.2f}%  {}".format(
            '', value, colored_diff, ratio, name))


def invest_advice(fund_code:str=None):
    _personal_choices = [fund_code] if fund_code else ['162605', '110022', '161903', '570008']
    for pc in _personal_choices:
        f = Fund(pc)
        f.printBasicInfo()
    show_sz_index()


if __name__ == '__main__':
    invest_advice()
