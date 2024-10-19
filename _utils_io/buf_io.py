from __future__ import annotations
from _utils_import import _utils_file, _utils_system
import sys, os, traceback
from io import BytesIO
import _utils_io

def run_func_with_output_to_buf(func, *args, print_to_stdout=False, pipe_prev=None, **kwargs) -> BytesIO:
    def print_bytes_to_buf(_bytes:bytes, buf: BytesIO):
        buf.write(_bytes)
        return True
    def print_bytes_to_stdout(_bytes):
        if not print_to_stdout:
            return True
        try:
            os.write(fd_stdout_origin, _bytes)
        except Exception: # fd_stdout_origin becomes invalid
            return False
        return True

    def listen_thread(fd_read, buf, pipe_prev=None):
            if pipe_prev is not None:
                if isinstance(pipe_prev, BytesIO):
                    out_bytes = _utils_io.read_from_bytes_io(pipe_prev)
                else:
                    pass # TODO
                if out_bytes is not None:
                    print_bytes_to_buf(out_bytes, buf)
            while True:
                out_bytes = os.read(fd_read, 1024)  # fd_read --> f
                if not print_bytes_to_buf(out_bytes, buf): break
                if not print_bytes_to_stdout(out_bytes): break

    # stdout/stderr --> BytesIO object
    fd_stdout_origin = os.dup(1)
    fd_stderr_origin = os.dup(2)
    fd_read, fd_write = os.pipe()
    os.dup2(fd_write, 1) # fd=1 / fd_write --> same_target
        # make a copy of fd=1, as fd_write
    os.dup2(fd_write, 2) # fd=2 / fd_write --> same_target
        # make fd=1 refer to same target as fd_write

    buf = BytesIO()
    # https://stackoverflow.com/questions/66784941/dup2-and-pipe-shenanigans-with-python-and-windows
    # avoid OSError: [WinError 1] on Windows
    sys.stdout.write = lambda z: os.write(sys.stdout.fileno(), z.encode() if hasattr(z,'encode') else z)
    sys.stderr.write = lambda z: os.write(sys.stderr.fileno(), z.encode() if hasattr(z,'encode') else z)

    _listen_thread = _utils_system.start_thread(
        listen_thread, fd_read=fd_read, buf=buf, pipe_prev=pipe_prev,
        daemon=True, join=False
    )
    try:
        func(*args, **kwargs)
    except Exception:
        error_str = traceback.format_exc()
        try:
            print(error_str)
        except Exception:
            pass
    
    _listen_thread.join(0.2) # wait for thread to handle all outputs

    # restore
    os.dup2(fd_stdout_origin, 1) # restore stdout to the terminal
    os.close(fd_stdout_origin)
    os.dup2(fd_stderr_origin, 2) # restore stdout to the terminal
    os.close(fd_stderr_origin)
    return buf


if __name__ == "__main__":
    import sys, os, pathlib
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
    dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
    dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
    sys.path += [
        dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
    ]
    from _utils_import import _utils_file
    import time
    with RedirectStdOutAndStdErrToBytesIO() as f:
        # print("RedirectStdOutAndStdErrToBytesIO. output to stdout and stderr")
        print("RedirectStdOutAndStdErrToBytesIO. output to stdout", file=sys.stdout)
        print("RedirectStdOutAndStdErrToBytesIO. output to stderr", file=sys.stderr)
        print("RedirectStdOutAndStdErrToBytesIO. output to sys.__stdout__", file=sys.__stdout__)
        print("RedirectStdOutAndStdErrToBytesIO. output to sys.__stderr__", file=sys.__stderr__)
        # time.sleep(1.0)

    data = read_from_string_io(f.buffer)
    print(data.decode("utf-8"))
    a = 1

    print("begin")
    import time
    with RedirectStdOutAndStdErrToFile(
        file_path=_utils_file.get_file_path_no_suffix(__file__) + "/stdout_stderr.txt",
        pipe_prev=f
    ):
        print("output to stdout and stderr")
        print("output to stdout", file=sys.stdout)
        print("output to stderr", file=sys.stderr)
        print("output to sys.__stdout__", file=sys.__stdout__)
        print("output to sys.__stderr__", file=sys.__stderr__)
        # time.sleep(1.0)
    print("end")
    time.sleep(1.0)
    a = 1