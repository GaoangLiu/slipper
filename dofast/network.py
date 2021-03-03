import socket
import urllib.request

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


# Network.is_good_proxy('localhost:9898')
