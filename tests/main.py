import dofast as df

# df.p("Yes. SUCCESS.")
# df.info("Hello")
# df.warning("Worning message")

# p("Hello world!")

import subprocess, sys

cipcc= df.shell('curl -s cip.cc')
df.p(cipcc)


# f = df.smartopen('https://raw.githubusercontent.com/drocat/stuff/master/2021/p.pac')
# for x in f[:10]:
#     print(x)

@df.logged(df.info, 'examples...')
def countdown(n):
    while n > 0:
        n-=1
        df.sleep(1)

countdown(3)
