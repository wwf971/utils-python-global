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

import threading
import select
import _utils_io

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
        """ write data from the pipe to the file in real-time using select """
        parent = self.parent
        with open(parent.file_path, 'wb') as f:
            self.f = f
            if parent.pipe_prev is not None:
                bytes_prev = _utils_io.read_from_string_io(parent.pipe_prev.buffer)
                if bytes_prev is not None:
                    if not self.write_output(bytes_prev, f):
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
    
class RedirectStdOutAndStdErrToFile(Redirect):
    def __init__(self, file_path=None, pipe_prev=None):
        self.file_path = file_path
        from _utils_import import _utils_file
        _utils_file.create_dir_for_file_path(file_path)
        self.pipe_prev = pipe_prev
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
