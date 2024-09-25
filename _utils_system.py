
import platform

def is_win():
    _platform = platform.platform().lower()
    return "windows" in _platform

def is_linux():
    _platform = platform.platform().lower()
    return "linux" in _platform

def is_macos():
    _platform = platform.platform().lower()
    return "darwin" in _platform