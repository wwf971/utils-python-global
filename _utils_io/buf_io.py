from __future__ import annotations
from _utils_import import _utils_file, _utils_system
import sys, os, traceback
from io import BytesIO
import _utils_io
import traceback

from typing import Any, Optional, Tuple, Callable

def run_func_with_output_to_buf(func, args=(), kwargs:dict={}, print_to_stdout=False, pipe_prev=None, **_kwargs) -> Tuple[BytesIO, Any]:
    kwargs.update(_kwargs)
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

    listen_thread = _utils_system.start_thread(
        listen_thread, fd_read=fd_read, buf=buf, pipe_prev=pipe_prev,
        dependent=True, join=False
    )
    func_return = None
    try:
        func_return = func(*args, **kwargs) # run func
    except Exception:
        error_str = traceback.format_exc()
        try:
            print(error_str)
        except Exception:
            pass
    
    listen_thread.join(0.2) # wait for thread to handle all outputs

    # restore
    os.dup2(fd_stdout_origin, 1) # restore stdout to terminal
    os.close(fd_stdout_origin)
    os.dup2(fd_stderr_origin, 2) # restore stdout to terminal
    os.close(fd_stderr_origin)
    return buf, func_return

class StdOutAndStdErrToBuf:
    def __init__(
        self,
        separate_stdout_stderr: bool = True,
        print_to_stdout: bool = False,
        pipe_prev: Optional[BytesIO] = None,
    ):
        self.print_to_stdout = print_to_stdout
        self.pipe_prev = pipe_prev
        self.func_return: Any = None
        self.separate_stdout_stderr = separate_stdout_stderr
    def __enter__(self) -> Tuple[BytesIO, Callable[[Callable, tuple, dict], Any]]:
        # save original stdout/stderr
        self.fd_stdout_origin = os.dup(1)
        self.fd_stderr_origin = os.dup(2)

        # redirect stdout/stderr to a pipe
        if self.separate_stdout_stderr:
            self.fd_read_out, fd_write_out = os.pipe()
            self.fd_read_err, fd_write_err = os.pipe()
            os.dup2(fd_write_out, 1)
            os.dup2(fd_write_err, 2)
        else:
            self.fd_read, self.fd_write = os.pipe()
            os.dup2(self.fd_write, 1)
            os.dup2(self.fd_write, 2)

        # patch sys.stdout.write and sys.stderr.write
        sys.stdout.write = lambda z: os.write(sys.stdout.fileno(), z.encode() if hasattr(z, 'encode') else z)
        sys.stderr.write = lambda z: os.write(sys.stderr.fileno(), z.encode() if hasattr(z, 'encode') else z)

        # start thread to listen on the read-end of the pipe
        if self.separate_stdout_stderr:
            self.buf_out = BytesIO()
            self.buf_err = BytesIO()
            self.thread_list = [
                _utils_system.start_thread(
                    self.listen_thread_func,
                    fd_read=self.fd_read_out,
                    buf=self.buf_out,
                    pipe_prev=self.pipe_prev,
                    dependent=True,
                    join=False,
                ),
                _utils_system.start_thread(
                    self.listen_thread_func,
                    fd_read=self.fd_read_err,
                    buf=self.buf_err,
                    pipe_prev=self.pipe_prev,
                    dependent=True,
                    join=False,
                )
            ]
            return self.buf_out, self.buf_err
        else:
            self.buf = BytesIO()
            self.thread_list = [
                _utils_system.start_thread(
                    self.listen_thread_func,
                    fd_read=self.fd_read,
                    buf=self.buf,
                    pipe_prev=self.pipe_prev,
                    dependent=True,
                    join=False,
                )
            ]
            return self.buf

    def listen_thread_func(self, fd_read, buf, pipe_prev=None):
        def print_bytes_to_buf(_bytes: bytes, buf: BytesIO):
            buf.write(_bytes)
            return True

        def print_bytes_to_stdout(_bytes):
            if not self.print_to_stdout:
                return True
            try:
                os.write(self.fd_stdout_origin, _bytes)
            except Exception:
                return False
            return True

        if pipe_prev is not None:
            if isinstance(pipe_prev, BytesIO):
                out_bytes = _utils_io.read_from_bytes_io(pipe_prev)
                if out_bytes is not None:
                    print_bytes_to_buf(out_bytes, buf)
            else:
                pass  # TODO

        while True:
            out_bytes = os.read(fd_read, 1024)
            if not out_bytes:
                break
            if not print_bytes_to_buf(out_bytes, buf):
                break
            if not print_bytes_to_stdout(out_bytes):
                break

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            os.close(self.fd_write)  # Signal EOF to reading thread
        except Exception:
            pass

        if exc_type is not None: # exit due to exception
            traceback_str = ''.join(traceback.format_exception(exc_type, exc_val, exc_tb))
            print(traceback_str, file=sys.stderr) # exception_str --> sys.stderr --> buf
        
        for thread in self.thread_list:
            thread.join(0.2)  # wait to flush all output

        try:
            os.dup2(self.fd_stdout_origin, 1)
            os.close(self.fd_stdout_origin)
            os.dup2(self.fd_stderr_origin, 2)
            os.close(self.fd_stderr_origin)
        except Exception:
            pass