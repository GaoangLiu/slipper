import dirtyfast as df

df.p("Yes. SUCCESS.")
df.info("Hello")
df.warning("Worning message")

# p("Hello world!")

import subprocess, sys


def shell(cmd: str) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                   shell=True).decode('utf8')


cipcc= df.shell('curl -s cip.cc')
df.p(cipcc)
