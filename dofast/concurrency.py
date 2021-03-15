import time
import threading
import queue
from typing import List


class Concurrency:
    def __init__(self):
        self._threads = {}
        self._results = []  # store return result

    def create_task(self, func, *args, timeout: float = float('inf')):
        t = threading.Thread(target=lambda q, a: q.append(func(*a)),
                             args=(self._results, args),
                             daemon=True)
        t.start()
        self._threads[t] = timeout

    def close(self):
        while len(self._threads) > 0:
            time.sleep(1)
            for t in list(self._threads.keys()):
                self._threads[t] -= 1
                if self._threads[t] <= 0:
                    t.join(timeout=0)
                    del self._threads[t]

                if not t.is_alive():
                    del self._threads[t]

        for v in self._results:
            print(v)

    def results(self) -> List:
        return self._results


def ss(tt: int):
    print('start', time.strftime('%X'))
    time.sleep(tt)
    print('done', time.strftime('%X'))
    return f"The time costed is {tt} "


def aa(a1, a2):
    time.sleep(a2)
    print(a1)
    return a1


if __name__ == "__main__":
    c = Concurrency()
    c.create_task(ss, 40, timeout=2)
    c.create_task(ss, 3)
    c.create_task(aa, 'fake argument', 4, timeout=1)
    c.close()
