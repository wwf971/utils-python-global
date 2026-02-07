from __future__ import annotations
from typing import TYPE_CHECKING
if __name__ == "__main__":
    from _print import (
        print_bytes_to_pipe,
        print_str_to_pipe,
        print_to_str
    )
else:
    from ._print import (
        print_bytes_to_pipe,
        print_str_to_pipe,
        print_to_str
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
    inc_indent = increased_indent
    def increase_indent(self):
        self.indent += 1
        return self
    def decrease_indent(self):
        if self.indent > 0:
            self.indent -= 1
        return self
    def print_with_increased_indent(self, *args, remove_repeating_spaces=False, **kwargs):
        if remove_repeating_spaces:
            _str = print_to_str(*args, **kwargs)
            import re
            _str = re.sub(r' +', ' ', _str)
            result = self.print(_str, indent=self.indent + 1, end="")
        else:
            result = self.print(*args, indent=self.indent + 1, **kwargs)
        return result
    print_with_inc_indent = print_with_increased_indent
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
    def print_title(self,
        title: str,
        symbol: str = '=',
        line_length: int = 60,
        indent=None,
        file=None,
        *args,
        empty_line_before: int = 0,
        empty_line_after: int = 0,
        **kwargs,

    ):
        if indent is None:
            indent = self.indent
        if file is None:
            pipe = self.pipe_default
        else:
            pipe = self.pipe[file]
        for _ in range(empty_line_before):
            print_str_to_pipe(pipe, "", indent=indent, end="\n")
        line = symbol * line_length
        print_str_to_pipe(pipe, line, indent=indent, end="\n", *args, **kwargs)
        print_str_to_pipe(pipe, title, indent=indent, end="\n", *args, **kwargs)
        print_str_to_pipe(pipe, line, indent=indent, end="\n", *args, **kwargs)
        for _ in range(empty_line_after):
            print_str_to_pipe(pipe, "", indent=indent, end="\n")
        return
    def print_without_repeating_spaces(self, _str: str, indent=None, file=None, *args, **kwargs):
        _str = print_to_str(_str, *args, **kwargs)
        import re
        _str = re.sub(r' +', ' ', _str)
        return self.print(_str, indent=indent, file=file, end="")


if __name__ == "__main__":
    import sys, os, pathlib
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    dir_path_1 = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
    dir_path_2 = pathlib.Path(dir_path_1).parent.absolute().__str__() + "/"
    dir_path_3 = pathlib.Path(dir_path_2).parent.absolute().__str__() + "/"
    dir_path_4 = pathlib.Path(dir_path_3).parent.absolute().__str__() + "/"
    dir_path_5 = pathlib.Path(dir_path_4).parent.absolute().__str__() + "/"
    paths = [ dir_path_current, dir_path_1, dir_path_2 , dir_path_3, dir_path_4, dir_path_5 ]
    sys.path[:0] = paths
    from _utils_import import _utils_io, _utils_file
    sys.path = sys.path[len(paths):]
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