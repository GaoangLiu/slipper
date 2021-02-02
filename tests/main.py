import dofast as df
#!/usr/bin/env python3.3
import os,sys


def findfile(prefix:str, dir:str="."):
    for relpath, dirs, files in os.walk(dir):
        for f in files:
            if prefix in f:
                full_path = os.path.join(dir, relpath, f)
                print(os.path.normpath(os.path.abspath(full_path)))


# df.p("Yes. SUCCESS.")
# df.info("Hello")
# df.warning("Worning message")

# p("Hello world!")

import subprocess, sys

cipcc= df.shell('curl -s cip.cc')
# df.p(cipcc)


# f = df.smartopen('https://raw.githubusercontent.com/drocat/stuff/master/2021/p.pac')
# for x in f[:10]:
#     print(x)

@df.logged(df.info, 'examples...')
def countdown(n):
    while n > 0:
        n-=1
        df.sleep(1)

# countdown(3)
findfile(sys.argv[1])
