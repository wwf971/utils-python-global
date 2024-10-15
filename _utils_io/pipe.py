from __future__ import annotations
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
            pipe = sys.stdout
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
    def print(self, *args, indent=None, **kwargs):
        if indent is None:
            indent = self.indent
        result = print_str_to_pipe(self.pipe, indent=indent, *args, **kwargs)
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
