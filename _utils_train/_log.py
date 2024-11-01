
class IntLog: # AccuracyAlongEpochBatchTrain
    def __init__(self, buf_size):
        if buf_size is not None:
            self.has_buf = True
            # collections.deque: FIFO(first-in-first-out) queue with max length.
            self.int_list = collections.deque([], maxlen=buf_size)
            self.batch_size_list = collections.deque([], maxlen=buf_size)
        else:
            self.has_buf = False
            self.int_list = []
            self.batch_size_list = []
    def append(self, data: float, batch_size: int):
        self.int_list.append(data)
        self.batch_size_list.append(batch_size)
        return self
    def report_avg(self):
        # assert len(self.PerformanceList) == len(self.SampleNumList)
        sample_num = 0
        int_sum = 0.0
        for index in range(len(self.int_list)):
            int_sum += self.int_list[index]
            sample_num += self.batch_size_list[index]
        return int_sum / sample_num
    def clear(self):
        if self.has_buf:
            raise NotImplementedError
        else:
            self.int_list.clear()
            self.batch_size_list.clear()

import collections
class FloatLog:
    def __init__(self, buf_size=None):
        if buf_size is not None:
            self.has_buf = True
            # collections.deque: FIFO(first-in-first-out) queue with max length.
            self.float_list = collections.deque([], maxlen=buf_size)
            self.batch_size_list = collections.deque([], maxlen=buf_size)
        else:
            self.has_buf = False
            self.float_list = []
            self.batch_size_list = []
    def clear(self):
        if self.has_buf:
            raise NotImplementedError
        else:
            self.float_list.clear()
            self.batch_size_list.clear()
    def append(self, data: float, batch_size: int):
        self.float_list.append(data)
        self.batch_size_list.append(batch_size)
        return self
    def report_avg(self):
        # assert len(self.PerformanceList) == len(self.SampleNumList)
        sample_num = 0
        float_sum = 0.0
        for index in range(len(self.float_list)):
            float_sum += self.float_list[index]
            sample_num += self.batch_size_list[index]
        return float_sum / sample_num

class TriggerFuncAtEveryFixedInterval:
    def __init__(self, interval, func, *Args, **kwargs):
        self.Args = Args
        self.kwargs = kwargs
        self.reset()
        self.func = func
        self.interval = interval
    def reset(self):
        self.count = 0
    def tick(self):
        self.count += 1
        if self.count >= self.interval:
            result = self.func(*self.Args, **self.kwargs)
            self.reset()
            return result
        else:
            result = None
        return result