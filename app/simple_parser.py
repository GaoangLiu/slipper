import sys
import requests
from operator import itemgetter
from typing import List
from tqdm import tqdm


class SimpleParser:
    """A simple argument parser"""
    help_msg = None

    def __init__(self):
        self.dict = {}

    def has_attribute(self, arg_names: List, excludes: List[str] = []) -> bool:
        """ Decide if any argument is present in the dict
        Example: self.has_attribute(['-gu', '--githubupload']) 
        :params excludes: list, exclusive arguments
        """
        b = any(e in self.dict for e in excludes)
        return not b and any(map(lambda an: an in self.dict, arg_names))

    def has_attr(self, arg_names: List, excludes: List[str] = []) -> bool:
        return self.has_attribute(arg_names, excludes)

    def parse_args(self) -> dict:
        args = sys.argv[1:]
        arg_name = None
        for a in args:
            if a.startswith('-'):
                self.dict[a] = []
                arg_name = a
            else:
                self.dict[arg_name].append(a)
        return self.dict

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
