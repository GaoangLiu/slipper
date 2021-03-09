import sys
import requests
import collections
from operator import itemgetter
from typing import List


def get_arg_name(arg_name: str) -> str:
    return arg_name.replace('-', '')


class SimpleParser:
    """A simple argument parser"""
    help_msg = None

    def __init__(self):
        self.__dict__ = collections.defaultdict(Attribute)

    def add_argument(self,
                     abbr: str = "",
                     full_arg: str = "",
                     default_value: str = "",
                     sub_args: List = [],
                     description: str = ""):
        """ Add arguments to object.
        :abbr: str, abbreviated argument, e.g., -dw could be an abbraviation of --download
        :full_arg: str, complete argument name, e.g., --download
        :default_value:, str, default value of argument
        :description: str, description of what the argument will invoke
        :sub_args:, dict, possible sub arguments.
        """
        assert full_arg != "", "Full argument name is prerequisite."
        abbr, full = get_arg_name(abbr if not abbr else abbr), get_arg_name(
            full_arg)

        attr = Attribute(default_value)
        setattr(self, full, attr)
        setattr(self, abbr, attr)

        for sub in sub_args:
            sub.sort(key=len)
            subattr = Attribute("")
            for sn in sub:
                setattr(attr, sn, subattr)

    def parse_args(self) -> None:
        """ Parse arguments from sys.argv. Two types of arguments:
        1. main argument, once decided, values of all other main argument is set to None
        2. sub argument.
        """
        mainarg, subarg, _attribute = None, None, {}
        sysargv = sys.argv[1:]
        for ele in sysargv:
            if ele.startswith('-'):
                subarg = get_arg_name(ele)
                if not mainarg:
                    mainarg = subarg
                    _attribute = getattr(self, mainarg)
                else:
                    _attribute = getattr(_attribute, subarg)
                # E.g., mainarg = 'cos', _attribute = Attribute(), then set _attribute['value'] = PLACEHOLDER
                if not getattr(_attribute, 'value'):
                    setattr(_attribute, 'value', "PLACEHOLDER")
            else:
                setattr(_attribute, 'value', ele)

        # No argument is passed in
        if mainarg is None:
            mainarg = '[-<>-]'
            setattr(self, mainarg, Attribute())

        for k, v in self.__dict__.items():
            if v != getattr(self, mainarg):
                setattr(self, k, None)

        # Set sub argument values to string
        for k, v in getattr(self, mainarg).__dict__.items():
            if not isinstance(v, str):
                setattr(getattr(self, mainarg), k, v.value)


class Attribute:
    """ Sub Attributes helper """
    def __init__(self, default_value: str = ""):
        self.__dict__ = collections.defaultdict()
        setattr(self, 'value', default_value)
