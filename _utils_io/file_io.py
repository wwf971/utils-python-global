from __future__ import annotations
from typing import TYPE_CHECKING
import sys, os
import select
import threading
import time
import traceback

from _utils_import import _utils_system
def run_func_with_output_to_file(func, file_path_stdout, *args, file_path_stderr=None, backend="dup", **kwargs):
    backend = backend.lower()
    if backend == "dup":
        run_func_with_output_to_file_dup(func, *args, file_path_stdout=file_path_stdout, file_path_stderr=file_path_stderr, **kwargs)
    elif backend == "simple":
        run_func_with_output_to_file_dup(func, *args, file_path_stdout=file_path_stdout, file_path_stderr=file_path_stderr, **kwargs)
    return

def run_func_with_output_to_file_dup(func, file_path_stdout, *args, file_path_stderr=None, pipe_previous=None, print_to_stdout=False, **kwargs):
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

    def listen_thread(fd_read, file_path, pipe_previous=None):
        with open(file_path, "wb") as f:
            if pipe_previous is not None:
                out_bytes = read_from_string_io(pipe_previous.buffer)
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
            listen_thread, fd_read=fd_read, file_path=file_path_stdout, pipe_previous=pipe_previous,
            daemon=True, join=False
        )
    else:
        _listen_thread_stdout = _utils_system.start_thread(
            listen_thread, fd_read=fd_read_stdout, file_path=file_path_stdout, pipe_previous=pipe_previous,
            daemon=True, join=False
        )
        _listen_thread_stderr = _utils_system.start_thread(
            listen_thread, fd_read=fd_read_stderr, file_path=file_path_stderr, pipe_previous=pipe_previous,
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
    return

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

class Redirect:
    def __init__(self, from_stdout=True, from_stderr=True, to_stdout=True):
        # before:
            # xxx --> sys.stdout --> fd=1 --> os
            # xxx --> sys.stderr --> fd=2 --> os
        # after:
            # xxx --> fd=1 --> fd_write | fd_read --thread--> file
            # xxx --> fd=2 --> fd_write | fd_read --thread--> file

        fd_read, fd_write = os.pipe() # fd: file descriptor
            # xxx --> fd_write | fd_read --> xxx
            # what is written to fd_write, can be read from fd_read
        if from_stdout:
            self.fd_stdout_origin = os.dup(1)
                # self.fd_stdout_origin will also write to what fd-1 is writing to
            os.dup2(fd_write, 1) # fd=1 --> fd_write
            self.redirect_stdout = True
        else:
            self.redirect_stdout = False

        if from_stderr:
            self.fd_stderr_origin = os.dup(2) # self.fd_stderr_origin will also write to what file descriptor 1 is writing to
            os.dup2(fd_write, 2) # file descriptor 2 --> fd_write
            self.redirect_stderr = True
        else:
            self.redirect_stderr = False
        
        # https://stackoverflow.com/questions/66784941/dup2-and-pipe-shenanigans-with-python-and-windows
        # avoid OSError: [WinError 1] on Windows
        sys.stdout.write = lambda z: os.write(sys.stdout.fileno(), z.encode() if hasattr(z,'encode') else z)
        sys.stderr.write = lambda z: os.write(sys.stderr.fileno(), z.encode() if hasattr(z,'encode') else z)
        
        self.fd_read = fd_read
        self.fd_write = fd_write
        self.to_stdout = to_stdout
    def __exit__(self, type, value, trace):
        self.is_terminated = True
        self.thread.join(0.1)
        # self.thread.join(0.1)
            # when with block ends, it seems thread will be deleted along with its parent.
            # thread might not have enough time to send all contents to true sys.stdout
        if self.redirect_stderr:
            os.dup2(self.fd_stdout_origin, 1)  # restore stdout to the terminal
            os.close(self.fd_stdout_origin)
        if self.redirect_stdout:
            os.dup2(self.fd_stderr_origin, 2)  # restore stdout to the terminal
            os.close(self.fd_stderr_origin)
        return

class RedirectThread(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    def run(self):
        """ Write data from the pipe to the file in real-time using select """
        parent = self.parent
        with open(parent.file_path, 'wb') as f:
            self.f = f
            if parent.pipe_previous is not None:
                output = read_from_string_io(parent.pipe_previous.buffer)
                if output is not None:
                    if not self.write_output(output, f):
                        return
            self.poll_output(f)
    def listen_output(self, f):
        parent = self.parent
        while True:
            # use select to wait for data on the pipe
            readable, _, _ = select.select([parent.fd_read], [], [], 1.0)
            if readable:
                output = os.read(parent.fd_read, 1024)  # Read from the pipe
                if not output:
                    break  # Exit if there's no more data
                else:
                    if not self.write_output(output, f):
                        break
            if parent.is_terminated is True:
                return
    def poll_output(self, f):
        parent = self.parent
        while True:
            output = os.read(parent.fd_read, 1024)  # read from pipe
            if not self.write_output(output, f):
                break
    def write_output(self, output, f):
        f.write(output)
        f.flush() # ensure data is written immediately
        if self.parent.to_stdout:
            try:
                os.write(self.parent.fd_stdout_origin, output)
            except Exception:
                return False
        return True

class RedirectStdOutAndStdErrToFile(Redirect):
    def __init__(self, file_path=None, pipe_previous=None):
        self.file_path = file_path
        from _utils_import import _utils_file
        _utils_file.create_dir_for_file_path(file_path)
        self.pipe_previous = pipe_previous
        super().__init__()
    def __enter__(self):
        self.is_terminated = False
        self.thread = RedirectThread(self)
        self.thread.daemon = True  # all alive thread are daemon --> python exit
        self.thread.start()
        return self.thread # if not, thread will be deleted on __exit__
    def __exit__(self, type, value, trace):
        self.is_terminated = True
        # self.thread.join()
        self.thread.join(0.1)
            # when with block ends, it seems thread will be deleted along with its parent.
            # thread might not have enough time to redirect contents from self.fd_read to to true sys.stdout
        if self.redirect_stderr: # restore stdout to the terminal
            os.dup2(self.fd_stdout_origin, 1)
            os.close(self.fd_stdout_origin)
        if self.redirect_stdout: # restore stdout to the terminal
            os.dup2(self.fd_stderr_origin, 2)
            os.close(self.fd_stderr_origin)
        return

def read_from_string_io(buffer):
    buffer.seek(0)  # Move cursor to the beginning
    data = buffer.read()  # Read the contents
    if not data:
        return None
    buffer.seek(0)  # Move cursor to the beginning again
    buffer.truncate(0)  # Clear the contents of the buffer
    return data

class RedirectStdOutAndStdErrToBytesIOThread(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    def run(self):
        """ write data from the pipe to the file in real-time using select """
        self.poll_output()
    def poll_output(self):
        parent = self.parent
        while True:
            output = os.read(parent.fd_read, 1024)  # os.read() is blocking.
            parent.buffer.write(output)
            parent.buffer.flush()
            if parent.is_terminated:
                return
    def listen_output(self):
        parent = self.parent
        while True:
            # select.select has delay.
            # PROBLEM: parent.__exit__() is called, this thread will be terminated.
            # might not be able to receive all outputs from parent.fd_read in time  
            # use select to wait for data on the pipe
            readable, _, _ = select.select([parent.fd_read], [], [], 1.0)
            if readable:
                output = os.read(parent.fd_read, 1024)  # Read from the pipe
                if not output:
                    break  # exit if there's no more data
                parent.buffer.write(output)
                parent.buffer.flush()

class RedirectStdOutAndStdErrToBytesIO(Redirect):    
    def __init__(self):
        super().__init__()
        from io import BytesIO
        self.buffer = BytesIO()
    def __enter__(self):
        self.is_terminated = False
        self.thread = RedirectStdOutAndStdErrToBytesIOThread(self)
        self.thread.daemon = True  # Ensure the thread exits when the main program exits
        self.thread.start()
        # return self.thread # if not, thread will be deleted on __exit_
        return self
    def __exit__(self, type, value, trace):
        self.is_terminated = True
        self.thread.join(0.1)
        # self.thread.join(0.1)
            # when with block ends, it seems thread will be deleted along with its parent.
            # thread might not have enough time to send all contents to true sys.stdout
        if self.redirect_stderr:
            os.dup2(self.fd_stdout_origin, 1)  # restore stdout to the terminal
            os.close(self.fd_stdout_origin)
        if self.redirect_stdout:
            os.dup2(self.fd_stderr_origin, 2)  # restore stdout to the terminal
            os.close(self.fd_stderr_origin)
        return

from _utils_import import _utils_file

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
        pipe_previous=f
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