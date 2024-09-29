import os
import platform

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
def start_thread(func, *args, daemon=False, block=False, **kwargs):
    """
    daemon=True   parent exit --> child exit
    daemon=False  parent exit --> child conitnue
    """
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.setDaemon(daemon)
    thread.start()
    if block:
        thread.join() # wait for child exit