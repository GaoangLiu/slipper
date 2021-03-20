import time
import threading
import queue
from collections import defaultdict
from typing import List, Tuple
from functools import partial


class Concurrency:
    def __init__(self):
        self._threads = {}
        self._tags = set()
        self.results = defaultdict(None)  # store return result

    def _add_tag(self, tag: str) -> str:
        """Add a tag for a thread. A thread tag works as a thread ID,
        but added before a thread is created.
        """
        if not tag or tag in self._tags:
            tag += str(time.perf_counter())
        self._tags.add(tag)
        return tag

    def is_thread_complete(self, tag: [str, List[str]]):
        '''check thread completeness by its tag'''
        def is_done(r: str) -> bool:
            return r in self.results

        return is_done(tag) if isinstance(tag, str) else all(map(is_done, tag))

    def create_task(self,
                    func: str,
                    *args,
                    timeout: float = float('inf'),
                    tag: str = "") -> None:
        tag = self._add_tag(tag or str(func))
        t = threading.Thread(target=lambda q, a: q.update({tag: func(*a)}),
                             args=(self.results, args),
                             daemon=True)
        t.start()
        self._threads[t] = timeout

    def close(self) -> None:
        _sleep_period = 0.01
        while len(self._threads) > 0:
            time.sleep(_sleep_period)

            for t in list(self._threads.keys()):
                self._threads[t] -= _sleep_period
                if self._threads[t] <= 0:
                    t.join(timeout=0)
                    del self._threads[t]

                if t in self._threads and not t.is_alive():
                    del self._threads[t]

    def __repr__(self):
        res = ''
        for t in self._tags:
            res += f'Thread tag: {t} | thread result: {self.results.get(t, None)}\n'
        return res


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
