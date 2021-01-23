from slipper import logger
import time

cnt = 1
while cnt < 10:
    logger.Logger().info("Transcript pending")
    cnt += 2
    time.sleep(2)

