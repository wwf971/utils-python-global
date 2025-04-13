from __future__ import annotations
from typing import TYPE_CHECKING
if __name__ == "__main__":
    from _print import (
        print_bytes_to_pipe,
        print_str_to_pipe,
    )
else:
    from ._print import (
        print_bytes_to_pipe,
        print_str_to_pipe,
    )

class _PipeOutIncreaseIndent:
    def __init__(self, parent: PipeOut):
        self.parent = parent
    def __enter__(self):
        self.parent.increase_indent()
    def __exit__(self, type, value, trace):
        self.parent.decrease_indent()

from collections import defaultdict
class PipeOut:
    def __init__(self, pipe=None):
        if pipe is None:
            import sys
            pipe = {
                "stdout": sys.stdout,
                "stderr": sys.stderr
            }
            self.pipe_default = sys.stdout

        if isinstance(pipe, list):
            assert len(pipe) > 0
            self.pipe_default = pipe[0]
            self.pipe = pipe
        elif isinstance(pipe, dict):
            assert len(pipe) > 0
            self.pipe = pipe
            self.pipe_default = list(pipe.values())[0]
        else:
            raise TypeError(pipe)

        self.pipe = pipe
        self.indent = 0
        self.print_every_counter = defaultdict(lambda: 0)
        return
    def increased_indent(self):
        return _PipeOutIncreaseIndent(self)
    def increase_indent(self):
        self.indent += 1
        return self
    def decrease_indent(self):
        if self.indent > 0:
            self.indent -= 1
        return self
    def print_with_increased_indent(self, *args, **kwargs):
        result = self.print(*args, indent=self.indent + 1, **kwargs)
        return result
    def print(self, *args, indent=None, file=None, **kwargs):
        if indent is None:
            indent = self.indent
        if file is None:
            pipe = self.pipe_default
        else:
            pipe = self.pipe[file]
        result = print_str_to_pipe(pipe, indent=indent, *args, **kwargs)
        return result
    def print_every(self, interval, *args, indent=None, **kwargs):
        if indent is None:
            indent = self.indent
        count = self.print_every_counter[interval]
        if count == 0:
            result = self.print(*args, indent=indent, **kwargs)
        else:
            result = None
        count += 1
        if count >= interval:
            count = 0
        self.print_every_counter[interval] = count
        return result
    def reset_print_every(self):
        self.print_every_counter = defaultdict(lambda: 0)
    def write(self, _str: str):
        # self.PrintWithoutIndent(Str)
        self.print(_str, end="")
    def write_bytes(self, _bytes: str, encoding='utf-8'):
        print_bytes_to_pipe(self.pipe, _bytes)


if __name__ == "__main__":
    import sys, os, pathlib
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    dir_path_1 = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
    dir_path_2 = pathlib.Path(dir_path_1).parent.absolute().__str__() + "/"
    dir_path_3 = pathlib.Path(dir_path_2).parent.absolute().__str__() + "/"
    dir_path_4 = pathlib.Path(dir_path_3).parent.absolute().__str__() + "/"
    dir_path_5 = pathlib.Path(dir_path_4).parent.absolute().__str__() + "/"
    sys.path += [
        dir_path_current, dir_path_1, dir_path_2 , dir_path_3, dir_path_4, dir_path_5
    ]
    from _utils_import import _utils_io, _utils_file
    
    file_path_stdout = _utils_file.get_file_path_current_no_suffix(__file__) + "-stdout.txt"
    file_path_stderr = _utils_file.get_file_path_current_no_suffix(__file__) + "-stderr.txt"
    dir_path_base = _utils_file.get_dir_path_current(__file__)

    
    with _utils_io.StdOutAndStdErrToFile(file_path_stdout=file_path_stdout, file_path_stderr=file_path_stderr):
        print("message --> sys.stdout --> file_path_stdout", file=sys.stdout)
        print("message --> sys.stderr --> file_path_stderr", file=sys.stderr)
        pipe_out = PipeOut()
        pipe_out.print("message --> stderr", file="stderr")
        with pipe_out.increased_indent():
            pipe_out.print("message 1 --> stderr", file="stderr")
            pipe_out.print("message 2 --> stderr", file="stderr")

        pipe_out.print("message --> stdout", file="stdout")
        with pipe_out.increased_indent():
            pipe_out.print("message 1 --> stdout", file="stdout")
            pipe_out.print("message 2 --> stdout", file="stdout")
        raise TypeError