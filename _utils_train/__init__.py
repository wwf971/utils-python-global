import sqlite3
from _utils_import import torch, np
import _utils

import random
def set_seed(seed: int=None, seed_random: int=None, seed_numpy: int=None, seed_torch: int=None):
    if seed_random is None and seed_numpy is None and seed_torch is None:
        seed_random = seed
        seed_numpy = seed
        seed_torch = seed

    if seed_random is not None:
        random.seed(seed_random)

    if seed_torch is not None:
        set_seed_for_torch(seed_torch)
    
    if seed_numpy is not None:
        set_seed_for_numpy(seed_numpy)

    return _utils.Dict()

def set_seed_for_numpy(seed: int):
    np.random.seed(seed)

def set_seed_for_torch(seed: int):
    torch.manual_seed(seed)

def GetDataBaseConnection(file_path):
    con = sqlite3.connect(file_path)
    return con

import collections
class FloatLog:
    def __init__(self, buf_size):
        # collections.deque: FIFO(first-in-first-out) queue with max length.
        self.float_list = collections.deque([], maxlen=buf_size)
        self.batch_size_list = collections.deque([], maxlen=buf_size)
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

class IntLog: # AccuracyAlongEpochBatchTrain
    def __init__(self, buf_size):
        # collections.deque: FIFO(first-in-first-out) queue with max length.
        self.int_list = collections.deque([], maxlen=buf_size)
        self.batch_size_list = collections.deque([], maxlen=buf_size)
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

class TriggerFuncAtEveryFixedInterval:
    def __init__(self, interval, Func, *Args, **kwargs):
        self.Args = Args
        self.kwargs = kwargs
        self.reset()
        self.Func = Func
        self.interval = interval
    def reset(self):
        self.count = 0
    def tick(self):
        self.count += 1
        if self.count >= self.interval:
            result = self.Func(*self.Args, **self.kwargs)
            self.reset()
            return result
        else:
            result = None
        return result
