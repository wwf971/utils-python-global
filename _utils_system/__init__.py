import os
import platform
import _utils_file
import _utils_system
import importlib

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

def get_current_process_pid():
    return os.getpid()

import threading
def start_thread(func, *args, daemon=False, join=False, **kwargs):
    """
    daemon=True   parent exit --> child exit
    daemon=False  parent exit --> child conitnue
        parent about to exit --> wait for all daemon=False child to exit --> parent really exit
    """
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.setDaemon(daemon) # the entire Python program exits when only daemon threads are left
    thread.start()
    if join:
        thread.join() # wait for child exit
    return thread
    # import _thread
    # try:
    #     _thread.start_new_thread(func, 
    #         args, # must be tuple. (xxx) is not a tuple. (xxx,) is a tuple.
    #     )
    # except:
    #     print ("Error: 无法启动线程")

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

def load_module_from_file_path(file_path_script):
    import importlib.util
    # load a .py script file as module
    _utils_file.check_file_exist(file_path_script)
    # load the module spec
    spec = importlib.util.spec_from_file_location("loaded_module", file_path_script)
    module_loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module_loaded)
    return module_loaded

from .python_script import (
    run_python_script,
    run_python_script_method
)