import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]
from _utils_import import datetime, _utils_io
from lib_datetime import (
    get_timezone,
    datetime_obj_change_timezone,
    datetime_obj_to_time_str,
)
if __name__ == "__main__":
    import datetime
    datetime_obj = datetime.datetime(2024, 8, 15, 11, 0, 0, 0, tzinfo=get_timezone(+8))

    pipe_out = _utils_io.PipeOut()
    pipe_out.print("BEFORE")
    with pipe_out.increased_indent():
        pipe_out.print("tzinfo:", datetime_obj.tzinfo)
        time_str = datetime_obj.strftime("%Y%m%d_%H%M%S%f")
        pipe_out.print("time  :", time_str)

    pipe_out.print("astimezone") # 改变时区和时间数值, 使得表示同一时间.
    with pipe_out.increased_indent():
        datetime_obj_new = datetime_obj.astimezone(get_timezone(-5))
            # datetime_obj_new and datetime_obj refer to same time point
        time_str = datetime_obj_new.strftime("%Y%m%d_%H%M%S%f")
        pipe_out.print("tzinfo:", datetime_obj_new.tzinfo)
        pipe_out.print("time  :", time_str)

    pipe_out.print("replace") # 只改变时区, 不改变时间数值.
    with pipe_out.increased_indent():
        datetime_obj_new = datetime_obj.replace(tzinfo=get_timezone(-5))
            # datetime_obj_new and datetime_obj have same o'clock.
        time_str = datetime_obj_new.strftime("%Y%m%d_%H%M%S%f")
        pipe_out.print("tzinfo:", datetime_obj_new.tzinfo)
        pipe_out.print("time  :", time_str)

    pipe_out.print("datetime_obj_change_timezone") # 只改变时区, 不改变时间数值.
    with pipe_out.increased_indent():
        datetime_obj_new = datetime_obj_change_timezone(datetime_obj, timezone=-5)
            # datetime_obj_new and datetime_obj have same o'clock.
        time_str = datetime_obj_new.strftime("%Y%m%d_%H%M%S%f")
        pipe_out.print("tzinfo:", datetime_obj_new.tzinfo)
        pipe_out.print("time  :", time_str)

    pipe_out.print("datetime_obj_to_time_str")
    with pipe_out.increased_indent():
        time_str = datetime_obj_to_time_str(datetime_obj, timezone=-5, format="%Y%m%d_%H%M%S%f")
        pipe_out.print("time  :", time_str)

    pipe_out.print("origin")
    with pipe_out.increased_indent():
        time_str = datetime_obj.strftime("%Y%m%d_%H%M%S%f")
        pipe_out.print("tzinfo:", datetime_obj.tzinfo)
        pipe_out.print("time  :", time_str)

    # datetime_obj_to_time_str("")
    pass