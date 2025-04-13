from __future__ import annotations
from typing import TYPE_CHECKING
import sys, os
import traceback
from _utils_import import _utils_file, _utils_system
import _utils_io
from io import StringIO, BytesIO

def run_func_with_output_to_file(
    func, file_path_stdout, 
    args=(), kwargs:dict={}, file_path_stderr=None, backend:str="dup",
    pipe_prev=None, **_kwargs
):
    kwargs.update(_kwargs)
    backend = backend.lower()
    if backend == "dup": # lower level implementation
        return run_func_with_output_to_file_dup(
            func, *args,
            file_path_stdout=file_path_stdout, file_path_stderr=file_path_stderr,
            pipe_prev=pipe_prev,
            **kwargs
        )
    elif backend == "simple":
        return run_func_with_output_to_file_simple(
            func, *args,
            file_path_stdout=file_path_stdout, file_path_stderr=file_path_stderr,
            **kwargs
        )
    else:
        raise ValueError(backend)

def run_func_with_output_to_file_dup(
    func, file_path_stdout, file_path_stderr=None,
    file_mode="wb", args=(),
    pipe_prev=None, print_to_stdout=False, **kwargs
):
    assert file_mode in ["ab", "wb"]
    def print_bytes_to_f(_bytes, f):
        f.write(_bytes)
        f.flush() # ensure data is written immediately
        return True
    def print_bytes_to_stdout(_bytes):
        if not print_to_stdout:
            return True
        try:
            os.write(fd_stdout_origin, _bytes)
        except Exception: # fd_stdout_origin becomes invalid
            return False
        return True

    def listen_thread(fd_read, file_path, pipe_prev=None):
        with open(file_path, file_mode) as f:
            if pipe_prev is not None:
                if isinstance(pipe_prev, BytesIO):
                    out_bytes = _utils_io.read_from_bytes_io(pipe_prev)
                elif isinstance(pipe_prev, StringIO):
                    out_bytes = _utils_io.read_from_string_io(pipe_prev)
                else:
                    pass # TODO
                if out_bytes is not None:
                    print_bytes_to_f(out_bytes, f)
            while True:
                out_bytes = os.read(fd_read, 1024)  # fd_read --> f
                if not print_bytes_to_f(out_bytes, f): break
                if not print_bytes_to_stdout(out_bytes): break

    # stdout/stderr --> file_path_stdout
    fd_stdout_origin = os.dup(1)
    fd_stderr_origin = os.dup(2)
    if file_path_stderr is None:
        fd_read, fd_write = os.pipe()
        os.dup2(fd_write, 1) # fd=1 / fd_write --> same_target
            # make a copy of fd=1, as fd_write
        os.dup2(fd_write, 2) # fd=2 / fd_write --> same_target
            # make fd=1 refer to same target as fd_write
    else:
        fd_read_stdout, fd_write_stdout = os.pipe()
        fd_read_stderr, fd_write_stderr = os.pipe()
        os.dup2(fd_write_stdout, 1) # fd=1 / fd_write_stdout --> same_target
            # make fd=1 refer to same target as fd_write_stdout
        os.dup2(fd_write_stderr, 2) # fd=2 / fd_write_stderr --> same_target
            # make fd=2 refer to same target as fd_write_stdout

    # https://stackoverflow.com/questions/66784941/dup2-and-pipe-shenanigans-with-python-and-windows
    # avoid OSError: [WinError 1] on Windows
    sys.stdout.write = lambda z: os.write(sys.stdout.fileno(), z.encode() if hasattr(z,'encode') else z)
    sys.stderr.write = lambda z: os.write(sys.stderr.fileno(), z.encode() if hasattr(z,'encode') else z)

    _utils_file.create_dir_for_file_path(file_path_stdout)
    if file_path_stderr is None:
        _listen_thread = _utils_system.start_thread(
            listen_thread, fd_read=fd_read, file_path=file_path_stdout, pipe_prev=pipe_prev,
            dependent=True, join=False
        )
    else:
        _listen_thread_stdout = _utils_system.start_thread(
            listen_thread, fd_read=fd_read_stdout, file_path=file_path_stdout, pipe_prev=pipe_prev,
            dependent=True, join=False
        )
        _listen_thread_stderr = _utils_system.start_thread(
            listen_thread, fd_read=fd_read_stderr, file_path=file_path_stderr, pipe_prev=pipe_prev,
            dependent=True, join=False
        )

    try:
        result = func(*args, **kwargs)
    except Exception:
        result = None
        error_str = traceback.format_exc()
        try:
            print(error_str)
        except Exception:
            pass
    
    if file_path_stderr is None:
        _listen_thread.join(0.2) # wait for thread to handle all outputs
    else:
        _listen_thread_stdout.join(0.2)
        _listen_thread_stderr.join(0.2)

    # restore
    os.dup2(fd_stdout_origin, 1) # restore stdout to the terminal
    os.close(fd_stdout_origin)
    os.dup2(fd_stderr_origin, 2) # restore stdout to the terminal
    os.close(fd_stderr_origin)
    return result

from typing import Optional
class StdOutAndStdErrToFile:
    def __init__(
        self,
        file_path_stdout: str,
        file_path_stderr: Optional[str] = None,
        pipe_prev=None, pipe_prev_out=None, pipe_prev_err=None,
        print_to_stdout=False,
        file_mode="wb"
    ):
        self.file_path_stdout = file_path_stdout
        self.file_path_stderr = file_path_stderr
        self.pipe_prev = pipe_prev
        self.pipe_prev_out = pipe_prev_out
        self.pipe_prev_err = pipe_prev_err
        self.print_to_stdout = print_to_stdout
        self.file_mode = file_mode
        assert self.file_mode in ["ab", "wb"]
        self.thread_list = []
        self._result = None

    def _print_bytes_to_f(self, _bytes, f):
        f.write(_bytes)
        f.flush()
        return True

    def _print_bytes_to_stdout(self, _bytes):
        if not self.print_to_stdout:
            return True
        try:
            os.write(self._fd_stdout_origin, _bytes)
        except Exception:
            return False
        return True

    def _listen_thread(self, fd_read, file_path, pipe_prev_list=None):
        with open(file_path, self.file_mode) as f:
            for pipe_prev in pipe_prev_list:
                if pipe_prev is not None:
                    if isinstance(pipe_prev, BytesIO):
                        out_bytes = _utils_io.read_from_bytes_io(pipe_prev)
                    elif isinstance(pipe_prev, StringIO):
                        out_bytes = _utils_io.read_from_string_io(pipe_prev)
                    else:
                        pass  # TODO
                    if out_bytes is not None:
                        self._print_bytes_to_f(out_bytes, f)
            while True:
                out_bytes = os.read(fd_read, 1024)
                if not self._print_bytes_to_f(out_bytes, f): break
                if not self._print_bytes_to_stdout(out_bytes): break

    def __enter__(self):
        self._fd_stdout_origin = os.dup(1)
        self._fd_stderr_origin = os.dup(2)

        if self.file_path_stderr is None:
            self._fd_read, fd_write = os.pipe()
            os.dup2(fd_write, 1)
            os.dup2(fd_write, 2)
        else:
            self._fd_read_out, fd_write_out = os.pipe()
            self._fd_read_err, fd_write_err = os.pipe()
            os.dup2(fd_write_out, 1)
            os.dup2(fd_write_err, 2)

        # avoid WinError on Windows
        sys.stdout.write = lambda z: os.write(sys.stdout.fileno(), z.encode() if hasattr(z, 'encode') else z)
        sys.stderr.write = lambda z: os.write(sys.stderr.fileno(), z.encode() if hasattr(z, 'encode') else z)

        _utils_file.create_dir_for_file_path(self.file_path_stdout)

        if self.file_path_stderr is None:
            pipe_prev_list = []
            if self.pipe_prev:
                pipe_prev_list.append(self.pipe_prev)
            if self.pipe_prev_out:
                pipe_prev_list.append(self.pipe_prev_out)
            if self.pipe_prev_err:
                pipe_prev_list.append(self.pipe_prev_err)

            thread = _utils_system.start_thread(
                self._listen_thread, fd_read=self._fd_read, file_path=self.file_path_stdout,
                pipe_prev=pipe_prev_list, dependent=True, join=False
            )
            self.thread_list.append(thread)
        else:
            pipe_prev_out_list = []
            if self.pipe_prev:
                pipe_prev_out_list.append(self.pipe_prev)
            if self.pipe_prev_out:
                pipe_prev_out_list.append(self.pipe_prev_out)
            thread_stdout = _utils_system.start_thread(
                self._listen_thread, fd_read=self._fd_read_out, file_path=self.file_path_stdout,
                pipe_prev_list=pipe_prev_out_list, dependent=True, join=False
            )
            pipe_prev_err_list = []
            if self.pipe_prev_err:
                pipe_prev_err_list.append(self.pipe_prev_err)
            thread_stderr = _utils_system.start_thread(
                self._listen_thread, fd_read=self._fd_read_err, file_path=self.file_path_stderr,
                pipe_prev_list=pipe_prev_err_list, dependent=True, join=False
            )
            self.thread_list.extend([thread_stdout, thread_stderr])
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None: # exit due to exception
            traceback_str = ''.join(traceback.format_exception(exc_type, exc_val, exc_tb))
            print(traceback_str, file=sys.stderr) # exception_str --> sys.stderr --> buf

        for thread in self.thread_list:
            thread.join(0.2)

        os.dup2(self._fd_stdout_origin, 1)
        os.dup2(self._fd_stderr_origin, 2)
        os.close(self._fd_stdout_origin)
        os.close(self._fd_stderr_origin)

def run_func_with_output_to_file_simple(func, file_path_stdout, *args, file_path_stderr=None, **kwargs):
    # might not correctly redirect output from low-level c library to file
        # as they directly write to fd(file descriptor)
    if file_path_stderr is not None:
            # stdout --> file_path_stdout
            # stderr --> file_path_stderr
        _utils_file.create_dir_for_file_path(file_path_stdout)
        _utils_file.create_dir_for_file_path(file_path_stderr)
        
        stdout_origin = sys.__stdout__
        stderr_origin = sys.__stderr__
        
        with open(file_path_stdout, "w", encoding='utf-8') as f:
            with open(file_path_stderr, "w", encoding='utf-8') as e:
                sys.__stdout__ = sys.stdout = f
                sys.__stderr__ = sys.stderr = e
                try:
                    func(args, **kwargs)
                except Exception:
                    error_str = traceback.format_exc()
                    e.write(error_str)

        sys.__stdout__ = sys.stdout = stdout_origin
        sys.__stderr__ = sys.stderr = stderr_origin

    else:
        # stdout/stderr --> file_path_stdout
        _utils_file.create_dir_for_file_path(file_path_stdout)
        
        stdout_origin = sys.__stdout__
        stderr_origin = sys.__stderr__
        
        with open(file_path_stdout, "w", encoding='utf-8') as f:
            sys.__stdout__ = sys.stdout = f
            sys.__stderr__ = sys.stderr = f
            try:
                func(args, **kwargs)
            except Exception:
                error_str = traceback.format_exc()
                f.write(error_str)

        sys.__stdout__ = sys.stdout = stdout_origin
        sys.__stderr__ = sys.stderr = stderr_origin

def text_file_to_str(file_path):
    file_path = _utils_file.check_file_exist(file_path)
    with open(file_path, "r") as f:
        text = f.read()
    return text

def str_to_text_file(text: str, file_path):
    file_path = _utils_file.create_dir_for_file_path(file_path)
    with open(file_path, 'w') as f:
        f.write(text)
    return

