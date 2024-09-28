
from __future__ import annotations
from _utils_import import datetime

# gmt time: utc time zone. not affected by daylight saving time.

from _utils_import import datetime
def datetime_obj_to_time_str(datetime_obj_utc, timezone: str=None, format="%Y%m%d_%H%M%S%f"):
    DateTimeObjLocal = datetime_obj_to_timezone(datetime_obj_utc, timezone=timezone)
    return DateTimeObjLocal.strftime(format)

def get_local_timezone():
    local_time_zone = datetime.datetime.utcnow().astimezone().tzinfo
    return local_time_zone # <class 'datetime.timezone'>

def datetime_obj_change_timezone(datetime_obj_utc: datetime.datetime, timezone:str=None) -> datetime.datetime:
    if timezone is not None:
        from dateutil import tz
        _timezone_utc = tz.gettz('UTC')
        datetime_obj_utc = datetime_obj_utc.replace(tzinfo=_timezone_utc)
        _timezone = get_local_timezone(timezone)
        datetime_obj_local = datetime_obj_utc.astimezone(_timezone)
        return datetime_obj_local
    else:
        raise NotImplementedError
    

