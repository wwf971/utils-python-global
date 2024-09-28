import time
import math

import _utils_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import datetime
    from dateutil import tz
else:
    datetime = _utils_import.LazyImport("datetime")
    tz = _utils_import.LazyFromImport("dateutil", "tz")
    timezone = _utils_import.LazyFromImport("datetime", "timezone")

# unix time stamp is always utc time zone
def get_unix_stamp_base():
    if globals().get("TimeStampBase") is None:
        global unix_stamp_base
        unix_stamp_base = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        return unix_stamp_base
    else:
        return unix_stamp_base

def datetime_obj_to_unix_stamp_float(datetime_obj) -> float:
    # return time.mktime(DataTimeObj.timetuple())
    # TimeStamp = DataTimeObj.timestamp() # >= Python 3.3
    time_diff = datetime_obj - get_unix_stamp_base()
    unix_stamp = time_diff.total_seconds()
    return unix_stamp

def get_current_unix_stamp_float() -> float:
    # return type: float, with millisecond precision.
    return datetime_obj_to_unix_stamp_float(
        datetime.datetime.utcnow() # caution. should use Greenwich Mean Time(GMT) here.
    )

def get_current_unix_stamp_int() -> int: # get unix time stamp
    return math.ceil(get_current_unix_stamp_float())

def unix_stamp_to_str(unix_stamp, timezone="utc", format=None):
    # unix_stamp始终是以UTC 1970/01/01为基准的.
    # 操作系统计算unix_stamp时, 会考虑到时区转换.
        # 即计算｢创建时间(UTC) - 1970/01/01(UTC)｣的秒数作为unix_stamp.
    timezone = timezone.lower()
    if timezone in ["utc"]:
        return unix_stamp_to_str_utc(unix_stamp, format=format)
    else:
        raise NotImplementedError

def unix_stamp_to_str_utc(unix_stamp:float, format=None):
    from datetime import datetime
    if format is None:
        format = '%Y-%m-%d %H:%M:%S(utc)'
    return datetime.utcfromtimestamp(unix_stamp).strftime(format)

def get_local_time_zone():
    local_time_zone = datetime.datetime.utcnow().astimezone().tzinfo
    return local_time_zone # <class 'datetime.timezone'>

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