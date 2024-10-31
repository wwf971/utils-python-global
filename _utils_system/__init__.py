import sys, os, time, traceback
import platform
from _utils_import import _utils_file, psutil
import _utils_system

_is_win = None
def is_win():
    global _is_win
    if _is_win is None:
        _platform = platform.platform().lower()
        _is_win = "windows" in _platform
    return _is_win

_is_linux = None
def is_linux():
    global _is_linux
    if _is_linux is None:
        _platform = platform.platform().lower()
        _is_linux = "linux" in _platform
    return _is_linux

_is_macos = None
def is_macos():
    global _is_macos
    if _is_macos is None:
        _platform = platform.platform().lower()
        _is_macos = "darwin" in _platform
    return _is_macos

def get_monitor_num():
    if is_win():
        import win32api # pip install pywin32
        import win32con
        monitor_num = win32api.GetSystemMetrics(win32con.SM_CMONITORS)
        return monitor_num
    else:
        raise NotImplementedError

def is_file_used_by_another_process(file_path):
    _utils_file.check_file_exist(file_path)
    if _utils_system.is_win():
        try: # windows only
            os.rename(file_path, file_path)
            return False
        except OSError:    # file is in use
            return True
    else:
        raise NotImplementedError

from ._module import (
    import_module_from_file,
    import_class_from_file
)

from .python_script import (
    run_python_script,
    run_python_script_method
)

from ._process import (
    process_exist,
    get_current_process_pid,
    exit_if_another_process_exit,
    exit_if_parent_process_exit
)

from .run_thread import (
    start_thread
)

from .run_process import (
    start_process,
    run_cmd_line_subprocess,
)

from .timeout import (
    run_func_with_timeout,
    run_func_with_timeout_multiple_trial,
    run_func_with_timeout_thread,
    run_func_with_timeout_wrapt
)