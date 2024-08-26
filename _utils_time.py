def unix_stamp_to_str(unix_stamp, timezone="utc"):
    # unix_stamp始终是以UTC 1970/01/01为基准的.
    # 操作系统计算unix_stemp时, 会考虑到时区转换.
        # 即计算｢创建时间(UTC) - 1970/01/01(UTC)｣的秒数作为unix_stamp.
    # 
    timezone = timezone.lower()
    if timezone in ["utc"]:
        return unit_stamp_to_str_utc(unix_stamp)
    else:
        raise NotImplementedError
def unit_stamp_to_str_utc(unix_stamp):
    from datetime import datetime
    return datetime.utcfromtimestamp(unix_stamp).strftime('%Y-%m-%d %H:%M:%S(utc)')