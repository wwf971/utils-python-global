
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

from file_io_cr import BytesBufCR
from _utils_import import _utils_file, _utils_io

file_path_stdout = _utils_file.get_file_path_current_no_suffix(__file__) + "~stdout.log"
file_path_stderr = _utils_file.get_file_path_current_no_suffix(__file__) + "~stderr.log"

import time
def child_func(start = 0, *args, **kwargs):
    _num = 0
    num = start
    while _num < 5:
        print("child: %s --> sys.stdout"%num, file=sys.stdout)
        print("child: %s --> sys.stderr"%num, file=sys.stderr)
        print("child: %s --> sys.__stdout__"%num, file=sys.__stdout__)
        print("child: %s --> sys.__stderr__"%num, file=sys.__stderr__)
        time.sleep(1)
        num += 1
        _num += 1

if __name__ == "__main__":
    buf = _utils_io.run_func_with_output_to_buf(
        child_func,
        file_path_stdout=file_path_stdout,
        file_path_stderr=file_path_stderr,
        print_to_stdout=False
    )

    _utils_io.run_func_with_output_to_file(
        child_func,
        start=6,
        file_path_stdout=file_path_stdout,
        file_path_stderr=None,
        pipe_prev=buf, # <-- buf
        print_to_stdout=True
    )