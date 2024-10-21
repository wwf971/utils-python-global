from __future__ import annotations
import sys

from .file_io import (
    text_file_to_str,
    str_to_text_file,
    run_func_with_output_to_file,
    run_func_with_output_to_file_dup,
    run_func_with_output_to_file_simple
)
from .file_io_cr import (
    run_func_with_output_to_file_dup_cr
)
from .buf_io import (
    run_func_with_output_to_buf
)
from ._print import (
    print_to_str,
    print_str_to_pipe
)

from .pipe import PipeOut

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from io import BytesIO

def read_from_bytes_io(buffer: BytesIO):
    buffer.seek(0)  # move cursor to the beginning
    data = buffer.read()  # Read the contents
    if not data:
        return None
    buffer.seek(0)  # move cursor to the beginning again
    buffer.truncate(0)  # clear the contents of the buffer
    return data
read_from_string_io = read_from_bytes_io # works for both BytesIO and StringIO

if __name__ == "__main__":
    pipe = PipeOut()
    pipe.print("aaa")
    with pipe.increased_indent():
        pipe.print("bbb")
    pipe.print("ccc")
    for index in range(100):
        pipe.print_every(10, "%d"%index)