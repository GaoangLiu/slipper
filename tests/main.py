import dirtyfast as xiu

xiu.p("Yes. SUCCESS.")
xiu.logger.info("Hello")
xiu.logger.error("Error message")

# p("Hello world!")

import subprocess, sys


def shell(cmd: str) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                   shell=True).decode('utf8')


res = xiu.shell("tree")
print(res)
    
