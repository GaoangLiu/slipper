# coding:utf-8
import logging
import os
import inspect
from logging.handlers import RotatingFileHandler
import colorlog  # 控制台日志输入颜色

log_colors_config = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}


class Logger:
    def __init__(self, logname: str = '/tmp/log.local.log'):
        self.logname = logname
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(levelname)s]- %(message)s',
            log_colors=log_colors_config)

        if self.logger.hasHandlers():  # To above duplicated lines
            return

        # 创建一个 FileHandler，写到本地
        fh = logging.handlers.TimedRotatingFileHandler(self.logname,
                                                       when='MIDNIGHT',
                                                       interval=1,
                                                       encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 创建一个StreamHandler,写到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

    @staticmethod
    def __get_call_info():
        stack = inspect.stack()
        cur = stack[3]
        fn, ln, func = cur[1:4]
        fn = "..." + fn[-10:]  # Restrict file path length
        return fn, func, ln

    def console(self, level: str, message: str, *args):
        LV = {
            'debug': self.logger.debug,
            'info': self.logger.info,
            'warn': self.logger.warning,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }
        f = LV.get(level, self.debug)
        message = "[{}.{}:{}] {}".format(*self.__get_call_info(), message)
        f(message, *args)

    def debug(self, message):
        self.console('debug', message)

    def info(self, message):
        self.console('info', message)

    def warning(self, message):
        self.console('warning', message)

    def error(self, message):
        self.console('error', message)

    def critical(self, message):
        self.console('critical', message)


def test():
    frames = inspect.stack()
    print(frames)
    Logger().info("Line 6666")


if __name__ == "__main__":
    log = Logger()
    log.info("测试1")
    log.debug("测试2")
    log.warning("warning")
    log.error("error")
    log.critical("critical")
    test()
