A package for faster Python programming. 

## Usage
```python
import slipper as sp
from logger import Logger

js = sp.jsonread('json_file.json')
sp.pp(js) # == pprint.pprint(js)


log = Logger()
log.info("Some info messages.")
```

## Install
python3 -m pip install -i https://test.pypi.org/simple/ xiu=="0.0.1a1"
