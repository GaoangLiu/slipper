import dirtyfast as df

df.p("Yes. SUCCESS.")
df.logger.info("Hello")
df.logger.error("Error message")

# p("Hello world!")

import subprocess, sys


def shell(cmd: str) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                   shell=True).decode('utf8')


client = df.Request.client
cipcc= df.shell('curl -s cip.cc')
df.p(cipcc)
