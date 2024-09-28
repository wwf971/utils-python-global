import time

class Timer:
    def __init__(self):
        self._start_time_last = None
        self._elapsed_time = 0.0
        self._is_running = False
        self._is_paused = False
    def start(self):
        if not self._is_running:
            self._elapsed_time = 0.0
            assert self._is_paused is False
        self._is_running = True
        self._is_paused = False
        self._start_time_last = time.time()
        return self
    def stop(self):
        if self._is_running:
            self._elapsed_time = time.time() - self._start_time_last
            self._is_running = False
            self._is_paused = False
        return self
    def pause(self):
        return Pauser(self)
    def _pause(self):
        assert self._is_running
        if not self._is_paused:
            self._elapsed_time += (time.time() - self._start_time_last)
            self._is_paused = True
    def get_time(self):
        return self._elapsed_time
    def report_time(self):
        print("Timer: %.3fs"%self._elapsed_time)

class Pauser:
    def __init__(self, parent: Timer):
        self.parent = parent
    def __enter__(self):
        # for param in self.parent.q.parameters(): param.requires_grad = False # lock q param
        self.parent._pause()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        # for param in self.parent.q.parameters(): param.requires_grad = True # unlock q param
        self.parent.start()