
import sys, os, pathlib

# Temporarily add current directory to sys.path for imports
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
sys.path.insert(0, dir_path_current)

try:
    from _utils_import import Dict, List
    from _utils_import import (
        _utils_file,
        _utils_image,
        _utils_io,
        _utils_system,
        _utils
    )
finally:
    # Clean up: remove the temporary path
    sys.path.pop(0)