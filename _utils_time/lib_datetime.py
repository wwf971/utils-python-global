
# don't name this file as date _datetime.py or datetime.py
    # results in conflicts with built-in datetime library

from __future__ import annotations
# from _utils_import import datetime
import datetime

# gmt time: utc time zone. not affected by daylight saving time.
def datetime_obj_to_time_str(datetime_obj, timezone: str=None, format="%Y%m%d_%H%M%S%f"):
    datetime_obj_new = datetime_obj_change_timezone(datetime_obj, timezone=timezone)
    return datetime_obj_new.strftime(format)

def get_local_timezone():
    local_time_zone = datetime.datetime.utcnow().astimezone().tzinfo
    return local_time_zone # <class 'datetime.timezone'>

def get_local_timezone_hour() -> int:
    timezone_local = get_local_timezone()
    utc_offset_src = timezone_local.utcoffset(datetime.datetime.now())
    _timezone_hour = utc_offset_src.total_seconds() / 3600  # Convert to hours
    timezone_hour = round(_timezone_hour)
    assert -0.1 < timezone_hour - _timezone_hour < 0.1
    return timezone_hour

def get_timezone(timezone_str, backend="pytz"):
    backend = backend.lower()
    if isinstance(timezone_str, str):
        timezone_str = timezone_str.lower()
    if timezone_str == "local":
        import tzlocal # pip install tzlocal
        _timezone_local = tzlocal.get_localzone()
        return _timezone_local

    if backend in ["pytz"]:
        return get_timezone_pytz(timezone_str)
    elif backend in ["datetime"]:
        return get_timezone_datetime(timezone_str)
    elif backend in["dateutil"]: # pip install python-dateutil
        return get_timezone_dateutil(timezone_str)
    else:
        raise NotImplementedError

def get_timezone_datetime(hour: int):
    from datetime import timedelta, timezone
    assert -12 <= hour <= 12
    _timezone = timezone(timedelta(hours=hour)) # NameError: name '_cmp' is not defined
    return _timezone

def get_timezone_pytz(timezone: int):
    import pytz
    if isinstance(timezone, int):
        hour = timezone
        assert -12 <= timezone <= 12
        if hour > 0:
            timezone_str = 'Etc/GMT-%d'%(timezone)
        elif hour < 0:
            timezone_str = 'Etc/GMT+%d'%(-timezone)
        else:
            _timezone = pytz.UTC
            return _timezone
    # Use the 'Etc/GMT+12' timezone for GMT-12
    _timezone = pytz.timezone(timezone_str)
    return _timezone
    # # Create an aware datetime object with the GMT-12 timezone
    # dt_gmt_minus_12 = datetime.now(gmt_minus_12)
    # print(dt_gmt_minus_12)
    # print(dt_gmt_minus_12.tzinfo)  # Output: Etc/GMT+12

def get_timezone_dateutil(hour: int):
    from dateutil import tz # pip install python-dateutil
    if hour > 0:
        _timezone = tz.gettz('Etc/GMT-%d'%(hour))
    elif hour == 0:
        _timezone = tz.gettz('Etc/GMT')
    else:
        # Use the 'Etc/GMT+12' timezone for GMT-12
        _timezone = tz.gettz('Etc/GMT+%d'%(-hour))
    return _timezone

def datetime_obj_change_timezone(datetime_obj: datetime.datetime, timezone:str=None, ) -> datetime.datetime:
    _timezone = get_timezone(timezone)
    datetime_obj_new = datetime_obj.astimezone(_timezone)
    return datetime_obj_new # datetime_obj and datetime_obj_new refer to same time point

    # datetime_obj_utc = datetime_obj_utc.replace(tzinfo=_timezone_utc)
    # _timezone = get_local_timezone(timezone)
    # return datetime_obj_local