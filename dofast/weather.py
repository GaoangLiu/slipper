import codefast as cf

from dofast.toolkits.telegram import tg_bot


class Weather:
    def __init__(self):
        self.api = 'http://t.weather.itboy.net/api/weather/city/101010100'

    def r_data(self):
        return cf.net.get(self.api).json()['data']['forecast'][0]

    @cf.utils.retry(initial_wait=5)
    @tg_bot(use_proxy=False)
    def daily(self):
        return '\n'.join('{:<10} {}'.format(k, v)
                         for k, v in self.r_data().items())


def entry():
    Weather().daily()


if __name__ == '__main__':
    wea = Weather()
    cf.say(wea.daily())
