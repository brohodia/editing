from time import perf_counter
from libraries.logging.algorithms.logger import get_logger


class Timer():
    def __init__(self):
        self._timers = {}
        self.disabled = False

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = True

    def reset(self):
        self._timers = {}

    def print_all(self):
        for timer_name, timer in self._timers.items():
            print(timer_name)
            timer_text = f"  {timer['total_time']:.2f}"
            if timer["active"]:
                timer_text += " - STILL RUNNING"
            print(timer_text)

    def get_timer(self, timer_name):
        return self._timers[timer_name]["total_time"]

    def reset_timer(self, timer_name):
        self._timers[timer_name] = {"total_time": 0, "active": False}

    def start(self, timer_name):
        if self.disabled is False:
            if timer_name not in self._timers:
                self.reset_timer(timer_name)
            if self._timers[timer_name]["active"]:
                pass
                raise ValueError(f"Can't start timer '{timer_name}' as it is already running")
            self._timers[timer_name]["start_time"] = perf_counter()
            self._timers[timer_name]["active"] = True

    def end(self, timer_name):
        if self.disabled is False:
            if self._timers[timer_name]["active"]:
                timer = self._timers[timer_name]
                end_time = perf_counter()
                start_time = timer["start_time"]
                marginal_time = end_time - start_time
                timer["total_time"] += marginal_time
                timer["active"] = False
                return marginal_time
            else:
                pass
                raise ValueError(f"Can't end timer '{timer_name}' as it is not running")

    def log_end(self, timer_name):
        if self.disabled is False:
            marginal_time = self.end(timer_name)
            log = get_logger()
            # log = init_log(hxd.ratingOutput.log.messages)
            log.info(f'{timer_name} executed in {marginal_time:.2f} s', exc_info=True)

timer = Timer()