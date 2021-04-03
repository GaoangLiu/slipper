import sys
import requests
import collections
from operator import itemgetter
from typing import List

PLACEHOLDER = "PLACEHOLDER"


class SimpleParser:
    """A simple argument parser"""
    def __init__(self):
        self.__dict__ = collections.defaultdict(Attribute)

    def input(self,
              abbr: str = "",
              full_arg: str = "",
              default_value: str = "",
              sub_args: List = [],
              description: str = ""):
        # alias of add argument
        self.add_argument(abbr,
                          full_arg,
                          default_value=default_value,
                          sub_args=sub_args,
                          description=description)

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
        assert full_arg != "", "Full argument name is required."
        full = full_arg.strip('-')
        abbr = abbr.strip('-') if abbr else full

        attribute_holder = _AttributeHolder(default_value)
        setattr(self, full, attribute_holder)
        setattr(self, abbr, attribute_holder)

        for sub_arg_list in sub_args:
            assert isinstance(sub_arg_list, list), "Sub args are list of list"

            _attribute = Attribute()
            for item in sorted(sub_arg_list, key=len):
                setattr(_AttributeHolder, item.strip('-'), _attribute)

    def parse_args(self) -> None:
        """ Parse arguments from sys.argv. Two types of arguments:
        1. main argument, once decided, values of all other main argument is set to None
        2. sub argument.
        """
        _main, _sub = None, None
        for item in sys.argv[1:]:
            if item.startswith('-'):
                _sub = item.strip('-')
                if not _main:
                    _main = _sub
                    if not self.__dict__[_sub].value:
                        self.__dict__[
                            _sub].value = PLACEHOLDER  # Assign default value.
                else:
                    _AttributeHolder.__dict__[_sub].value = PLACEHOLDER
            else:
                if _main == _sub:
                    self.__dict__[_main].value = item
                else:
                    _AttributeHolder.__dict__[_sub].value = item

        # When no argument is passed in, forge a main argument.
        if not _main:
            _main = PLACEHOLDER
            setattr(self, _main, None)

        for _other in self.__dict__.keys():  # set value of other arg to None
            if getattr(self, _other) != getattr(self, _main):
                setattr(self, _other, None)


class Attribute:
    """Final node of argparse to get value directly with dot notation."""
    def __init__(self, value: str = ""):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value: str) -> None:
        self.value = value


class _AttributeHolder(object):
    def __init__(self, value: str = ""):
        self.value = value
