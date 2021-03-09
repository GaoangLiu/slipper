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

    def has_attribute(self, arg_names: List, excludes: List[str] = []) -> bool:
        """ Decide if any argument is present in the dict
        Example: self.has_attribute(['-gu', '--githubupload']) 
        :params excludes: list, exclusive arguments
        """
        b = any(e in self.dict for e in excludes)
        return not b and any(map(lambda an: an in self.dict, arg_names))

    def has_attr(self, arg_names: List, excludes: List[str] = []) -> bool:
        return self.has_attribute(arg_names, excludes)

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
        self.__dict__[full] = attr
        self.__dict__[abbr] = attr

        for sub in sub_args:
            sub.sort(key=len)
            subattr = Attribute("")            
            for sn in sub:
                attr.__dict__[sn] = subattr

    def parse_args(self) -> None:
        main_arg, cur_arg, sub_attr = None, None, {}
        sysargv = sys.argv[1:]
        for ele in sysargv:
            if ele.startswith('-'):
                cur_arg = get_arg_name(ele)
                if not main_arg:
                    main_arg = cur_arg
                sub_attr = self.__dict__[main_arg]
            else:
                sub_attr.__dict__[cur_arg].value = ele
        
        # Set sub argument values to string
        for k, v in self.__dict__[main_arg].__dict__.items():
            # self.__dict__[main_arg].__dict__[k] = v.value
            if not isinstance(v, str):
                self.__dict__[main_arg].__dict__[k]=v.value

    def fetch_value(self,
                    arg_names: List,
                    default_value=None,
                    return_list: bool = False) -> str:
        """Return correspomding argument values. 
        By now, we assume each key corresponds to only one value. 
        We may need multiple values in the future.
        """
        for key in arg_names:
            if key in self.dict and len(self.dict[key]):
                return self.dict[key] if return_list else self.dict[key][0]
        return default_value

    def set_default(self, arg_name: str, value: str):
        """Set a default value for arg_name if arg_name is specified.
        """
        if arg_name in self.dict:
            self.dict[arg_name].append(value)


class Attribute:
    """ Sub Attributes helper """
    def __init__(self, default_value: str = ""):
        self.__dict__ = collections.defaultdict()
        self.__dict__['value'] = default_value
