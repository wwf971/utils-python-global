import _utils_import
from _utils_import import datetime
import _utils_time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dateutil import tz
else:
    tz = _utils_import.LazyFromImport("dateutil", "tz")
    timezone = _utils_import.LazyFromImport("datetime", "timezone")
import math

# unix time stamp is always based on utc time zone
# unix_stamp: float.

def get_unix_stamp_base_datetime_obj() -> datetime.date:
    if globals().get("TimeStampBase") is None:
        global unix_stamp_base
        unix_stamp_base = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        return unix_stamp_base
    else:
        return unix_stamp_base

def unix_stamp_to_datetime_obj(unix_stamp: float) -> datetime.datetime:
    # unix_stamp: float or int. unit: second.
    # millisecond is supported, and will not be floored.
    datetime_obj = get_unix_stamp_base_datetime_obj() + datetime.timedelta(seconds=unix_stamp)
    return datetime_obj # utc/gmt+0
    # might throw error for out of range time stamp.
    # DateTimeObj = date.fromtimestamp(TimeStamp)

def datetime_obj_to_unix_stamp(datetime_obj) -> float:
    # return time.mktime(DataTimeObj.timetuple())
    # TimeStamp = DataTimeObj.timestamp() # >= Python 3.3
    time_diff = datetime_obj - get_unix_stamp_base_datetime_obj()
    unix_stamp = time_diff.total_seconds()
    return unix_stamp

def get_current_unix_stamp() -> float:
    # return type: float, with millisecond precision.
    return datetime_obj_to_unix_stamp(
        datetime.datetime.utcnow() # caution. should use Greenwich Mean Time(GMT) here.
    )

def get_current_unix_stamp_int() -> int: # get unix time stamp
    return math.ceil(get_current_unix_stamp())

def unix_stamp_to_time_str(unix_stamp: float, timezone: str="local", format="%Y%m%d_%H%M%S%f"):
    # unix_stamp始终是以UTC 1970/01/01为基准的.
    # 操作系统计算unix_stamp时, 会考虑到时区转换.
        # 即计算｢创建时间(UTC) - 1970/01/01(UTC)｣的秒数作为unix_stamp.
    timezone = timezone.lower()
    if timezone in ["local"]:
        return unix_stamp_to_time_str_local(unix_stamp, format=format)
    elif timezone in ["utc", "greenwich", "utc+0", "utc0"]: # not affected by daylight saving time
        return unix_stamp_to_time_str_utc(unix_stamp, timezone=timezone, format=format)
    else:
        raise Exception

def unix_stamp_to_time_str_local(unix_stamp: float, format="%Y%m%d_%H%M%S%f"):
    if isinstance(unix_stamp, int):
        unix_stamp = unix_stamp * 1.0
    datetime_obj = unix_stamp_to_datetime_obj(unix_stamp)
    time_str = _utils_time.datetime_obj_to_time_str(datetime_obj, timezone=timezone, format=format)
    return time_str

def unix_stamp_to_time_str_utc(unix_stamp:float, format="%Y%m%d_%H%M%S%f"):
    return datetime.datetime.utcfromtimestamp(unix_stamp).strftime(format)