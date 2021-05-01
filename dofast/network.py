import socket
import urllib.request
import pprint
from .config import decode

socket.setdefaulttimeout(3)


class Network:
    @classmethod
    def is_good_proxy(cls, proxy: str) -> bool:
        """Check whether this proxy is valid or not"""
        try:
            pxy = {'http': proxy}
            proxy_handler = urllib.request.ProxyHandler(pxy)
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            sock = urllib.request.urlopen(
                'http://www.google.com')  # change the url address here
        except urllib.error.HTTPError as e:
            print('Error code: ', e.code)
            return False
        except Exception as detail:
            print("ERROR:", detail)
            return False
        return True

    def ipcheck(self, proxy: str) -> None:
        if self.is_good_proxy(proxy):
            print("")


# ========================================= Twitter API
class Twitter:
    def __init__(self):
        try:
            import twitter
        except ImportError:
            from pip._internal import main as pip
            pip(['install', '--user', 'python-twitter'])
            import tweepy

        self.api = twitter.Api(
            consumer_key=decode('consumer_key'),
            consumer_secret=decode('consumer_secret'),
            access_token_key=decode('access_token'),
            access_token_secret=decode('access_token_secret'),
            proxies={'http': decode('http_proxy')})

    def hi(self):
        print('hi, twitter.')

    def post_status(self, text: str, media=[]):
        resp = self.api.PostUpdate(text, media=media)
        print("Text  : {}\nMedia : {}\nResponse:".format(text, media))
        pprint.pprint(resp)
