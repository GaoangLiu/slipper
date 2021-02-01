import requests
import sys
import bs4
import string
import re


def get_emoji(emoji):
    res = requests.Session().get(f'https://emojipedia.org/search/?q={emoji}',
                                 proxies={'http': 'http://cn.ddot.cc:51170'})
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    for h in soup.find_all('h2'):
        if h.find('span'):
            text = h.text.strip()
            print("{:>5} {:<10}".format(text[0], text[1:]))


class YouDao():
    def _get_header(self):
        headers = {}
        headers[
            "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@6.002}"
        headers[
            "Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        return headers

    def search_word(self, kw='novice'):
        s = requests.Session()
        url = 'http://dict.youdao.com/w/{}'.format('%20'.join(kw.split()))
        res = s.get(url, headers=self._get_header())
        soup = bs4.BeautifulSoup(res.text, 'lxml')

        trans = soup.findAll('div', class_='trans-container')

        if len(trans) == 0:
            print("**Sorry, but no translation was found.**")
            return
        """ Chinese to English """
        for span in soup.findAll('span', class_='contentTitle'):
            if kw[0] in string.ascii_lowercase:  # Only print this for Chinese word
                continue

            trans = span.text.replace(";", '').strip()
            if trans[-1] in string.ascii_lowercase:
                print(trans)
        """ English to Chinese """
        ul = soup.findAll('ul')[1]
        for li in ul.findAll('li'):
            print('\t{}'.format(li.text))

        for div in soup.findAll('div',
                                {'class': {'examples', 'collinsMajorTrans'}}):
            # print(div.text)
            con = re.sub(r'(\s+)', ' ', div.text.strip())
            print('\t{}'.format(con))
            if div.attrs['class'][0] == 'examples':
                print('')


YouDao().search_word("nice")
YouDao().search_word("日本")
