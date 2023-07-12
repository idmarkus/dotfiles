import time


class Perf:
    def __init__(self, name):
        self._start = self._t = time.perf_counter_ns()
        self._name = name
        # print(f"{name} - - -", flush=True)

    def _get_dt(self, t):
        dt = "{:07}".format(time.perf_counter_ns() - t)
        return "{}.{}".format(dt[:-6], dt[-6:])

    def step(self, subname):
        print(f"  {subname}\t  {self._get_dt(self._t)} ms", flush=True)
        self._t = time.perf_counter_ns()

    def __del__(self):
        print(f"{self._name} : :\t{self._get_dt(self._start)} ms", flush=True)
