from __future__ import annotations
import sys

from .file_io import (
    RedirectStdOutAndStdErrToFile,
    RedirectStdOutAndStdErrToBytesIO,
    text_file_to_str,
    str_to_text_file,
    run_func_with_output_to_file,
    run_func_with_output_to_file_dup,
    run_func_with_output_to_file_simple
)

from .file_io_cr import (
    run_func_with_output_to_file_dup_cr
)

from ._print import (
    print_to_str,
    print_str_to_pipe
)

from .pipe import PipeOut

if __name__ == "__main__":
    pipe = PipeOut()
    pipe.print("aaa")
    with pipe.increased_indent():
        pipe.print("bbb")
    pipe.print("ccc")
    for index in range(100):
        pipe.print_every(10, "%d"%index)