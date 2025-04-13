import sys
from io import StringIO
def print_to_str(*args, **kwargs):
    # faster than reusing.
    # https://stackoverflow.com/questions/4330812/how-do-i-clear-a-stringio-object
    print_buf = StringIO()
    print_buf.seek(0)
    print_buf.truncate(0)
    print(*args, **kwargs, file=print_buf) # file=None ensures file is not in **kwargs
    str_ = print_buf.getvalue()
    print_buf.flush()
    del print_buf
    return str_

def print_bytes_to_pipe(pipe, _bytes: bytes, encoding='utf-8'):
    if hasattr(pipe, "buffer"):
        pipe.buffer.write(_bytes)
    else:
        pipe.write(_bytes.decode(encoding))

def print_str_to_pipe(pipe, *args, indent=None, **kwargs):
    _str = print_to_str(*args, **kwargs)
    if indent is None:
        indent = 0
    _print_str_to_pipe(pipe, _str, indent=indent)

def _print_str_to_pipe(
        pipe,
        _str: str,
        indent=None,
        flush=True,
        indent_str="    ", # "\t"
        encoding="utf-8"
    ):
    if indent is None:
        indent = 0
    if indent > 0:
        if _str.endswith("\n"):
            IsEndWithNewLine = True
            _str = _str.rstrip("\n")
        else:
            IsEndWithNewLine = False
        str_list = _str.split("\n")
        for index, str_line in enumerate(str_list):
            str_list[index] = "".join([indent_str for _ in range(indent)] + [str_line])
        _str = "\n".join(str_list)
        if IsEndWithNewLine:
            _str = _str + "\n"

    if hasattr(pipe, "write"):
        # <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>
        pipe.write(_str)
    elif hasattr(pipe, "buffer"):
        pipe.buffer.write(_str.encode(encoding))
    else:
        raise Exception

    if flush and hasattr(pipe, "flush"):
        try:
            pipe.flush()
        except Exception:
            pass

def write_utf8_to_stdout(str_print, indent:int=None):
    if indent is not None:
        assert isinstance(indent, int)
        str_list = str_print.split("\n")
        for index, _str in enumerate(str_list):
            write_utf8_to_stdout("    " * indent + _str + "\n")
        return
    else:
        bytes_print = str_print.encode("utf-8")
        try:
            sys.__stdout__.buffer.write(bytes_print)
        except Exception:
            pass # broken pipe