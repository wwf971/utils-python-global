from __future__ import annotations
from typing import TYPE_CHECKING
import sys, os
import select
import threading
import time

class Redirect:
    def __init__(self, from_stdout=True, from_stderr=True, to_stdout=True):
        read_fd, write_fd = os.pipe() # fd: file descriptor
        if from_stdout:
            self.fd_stdout_temp = os.dup(1) # self.fd_stdout_temp will also write to what file descriptor 1 is writing to
            os.dup2(write_fd, 1) # file descriptor 1 --> write_fd
            self.redirect_stdout = True
        else:
            self.redirect_stdout = False

        if from_stderr:
            self.fd_stderr_temp = os.dup(2) # self.fd_stderr_temp will also write to what file descriptor 1 is writing to
            os.dup2(write_fd, 2) # file descriptor 2 --> write_fd
            self.redirect_stderr = True
        else:
            self.redirect_stderr = False
        
        # https://stackoverflow.com/questions/66784941/dup2-and-pipe-shenanigans-with-python-and-windows
        # avoid OSError: [WinError 1] on Windows
        sys.stdout.write = lambda z: os.write(sys.stdout.fileno(),z.encode() if hasattr(z,'encode') else z)
        sys.stderr.write = lambda z: os.write(sys.stderr.fileno(),z.encode() if hasattr(z,'encode') else z)
        
        self.read_fd = read_fd
        self.write_fd = write_fd
        self.to_stdout = to_stdout
    def __exit__(self, type, value, trace):
        self.is_terminated = True
        self.thread.join(0.1)
        # self.thread.join(0.1)
            # when with block ends, it seems thread will be deleted along with its parent.
            # thread might not have enough time to send all contents to true sys.stdout
        if self.redirect_stderr:
            os.dup2(self.fd_stdout_temp, 1)  # restore stdout to the terminal
            os.close(self.fd_stdout_temp)
        if self.redirect_stdout:
            os.dup2(self.fd_stderr_temp, 2)  # restore stdout to the terminal
            os.close(self.fd_stderr_temp)
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
            # self.poll_output(f)
            self.poll_output(f)
    def listen_output(self, f):
        parent = self.parent
        while True:
            # use select to wait for data on the pipe
            readable, _, _ = select.select([parent.read_fd], [], [], 1.0)
            if readable:
                output = os.read(parent.read_fd, 1024)  # Read from the pipe
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
            output = os.read(parent.read_fd, 1024)  # Read from the pipe
            if not self.write_output(output, f):
                break
    def write_output(self, output, f):
        f.write(output)
        f.flush() # ensure data is written immediately
        if self.parent.to_stdout:
            try:
                os.write(self.parent.fd_stdout_temp, output)
            except Exception:
                return False
        return True

class RedirectStdOutAndStdErrToFile(Redirect):
    def __init__(self, file_path=None, pipe_previous=None):
        assert file_path is not None
        self.file_path = file_path
        from _utils_import import _utils_file
        _utils_file.create_dir_for_file_path(file_path)
        self.pipe_previous = pipe_previous
        super().__init__()
    def __enter__(self):
        self.is_terminated = False
        self.thread = RedirectThread(self)
        self.thread.daemon = True  # Ensure the thread exits when the main program exits
        
        self.thread.start()
        # return self.thread # if not, thread will be deleted on __exit_
        return self.thread
    def __exit__(self, type, value, trace):
        self.is_terminated = True
        # self.thread.join()
        self.thread.join(0.1)
            # when with block ends, it seems thread will be deleted along with its parent.
            # thread might not have enough time to redirect contents from self.read_fd to to true sys.stdout
        if self.redirect_stderr:
            os.dup2(self.fd_stdout_temp, 1)  # restore stdout to the terminal
            os.close(self.fd_stdout_temp)
        if self.redirect_stdout:
            os.dup2(self.fd_stderr_temp, 2)  # restore stdout to the terminal
            os.close(self.fd_stderr_temp)
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
            output = os.read(parent.read_fd, 1024)  # os.read() is blocking.
            parent.buffer.write(output)
            parent.buffer.flush()
            if parent.is_terminated:
                return
    def listen_output(self):
        parent = self.parent
        while True:
            # select.select has delay.
            # PROBLEM: parent.__exit__() is called, this thread will be terminated.
            # might not be able to receive all outputs from parent.read_fd in time  
            # use select to wait for data on the pipe
            readable, _, _ = select.select([parent.read_fd], [], [], 1.0)
            if readable:
                output = os.read(parent.read_fd, 1024)  # Read from the pipe
                if not output:
                    break  # exit if there's no more data
                parent.buffer.write(output)
                parent.buffer.flush()

class RedirectStdOutAndStdErrToBytesIO(Redirect):    
    def __init__(self):
        super().__init__()
        from io import StringIO, BytesIO
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
            os.dup2(self.fd_stdout_temp, 1)  # restore stdout to the terminal
            os.close(self.fd_stdout_temp)
        if self.redirect_stdout:
            os.dup2(self.fd_stderr_temp, 2)  # restore stdout to the terminal
            os.close(self.fd_stderr_temp)
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
        file_path=_utils_file.get_file_path_without_suffix(__file__) + "/stdout_stderr.txt",
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