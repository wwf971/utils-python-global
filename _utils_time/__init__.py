import time
import math

import _utils_import
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from dateutil import tz
# else:
#     datetime = _utils_import.lazy_import("datetime")
#     tz = _utils_import.LazyFromImport("dateutil", "tz")
#     timezone = _utils_import.LazyFromImport("datetime", "timezone")

from .timer import Timer, Pauser
from .lib_datetime import (
    datetime_obj_to_time_str,
    get_local_timezone,
    get_local_timezone_hour,
    datetime_obj_change_timezone,
    get_timezone, get_local_timezone,
)

from .unix import (
    get_unix_stamp_base_datetime_obj,
    unix_stamp_to_datetime_obj,
    get_current_unix_stamp,
    get_current_unix_stamp_int,
    unix_stamp_to_time_str,
    unix_stamp_to_time_str_local,
    get_unix_stamp_from_ymd_hms
)

def get_time_str_current(
    offset=0, # unit: second
    timezone="local",
    format=None
):
    if format is None:
        return get_time_str_current_ymd8_hms8(offset=offset, timezone=timezone)

    unix_stamp_current = get_current_unix_stamp() + offset
    time_str_current = unix_stamp_to_time_str(unix_stamp_current, timezone=timezone, format="%Y%m%d_%H%M%S")
    return time_str_current # YYmmdd_hhmmss

def get_time_str_current_local():
    from datetime import datetime, timezone, timedelta
    timezone_int = get_local_timezone_hour()
    unix_stamp = get_current_unix_stamp_int()
    now = datetime.now(timezone(timedelta(hours=timezone_int)))
    time_str = now.strftime(f'%Y/%m/%d %H:%M UTC{timezone_int:+03d} UNIX{unix_stamp:+d}')
    return time_str

def unix_stamp_to_time_str_ymd8_hms8(
    unix_stamp,
    timezone="local",
):
    time_str = unix_stamp_to_time_str(unix_stamp, timezone=timezone, format="%Y%m%d_%H%M%S%f")
    return time_str[:-4] # YYmmdd_hhmmss(ms2digit)

def get_time_str_current_ymd8_hms8(
    offset=0, # unit: second
    timezone="local",
):
    unix_stamp_current = get_current_unix_stamp() + offset
    time_str_current = unix_stamp_to_time_str(unix_stamp_current, timezone=timezone, format="%Y%m%d_%H%M%S%f")
    return time_str_current[:-4] # YYmmdd_hhmmss(ms2digit)

