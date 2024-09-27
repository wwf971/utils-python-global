if __name__ == "__main__":
    import sys, os, pathlib
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
    dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
    dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
    sys.path += [
        dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
    ]
    from file_io import RedirectStdOutAndStdErrToFile, RedirectThread, read_from_string_io
else:
    from .file_io import RedirectStdOutAndStdErrToFile, RedirectThread, read_from_string_io

import os
class ByteBufferCR:
    # byte buffer that deals with CR(carriage return) just like in terminals
    def __init__(self, buffer_size=65536):
        self.buffer = bytearray(1024)
        self.buffer_size_current = len(self.buffer)
        self.index_start = 0
        self.index_write = 0
        self.index_end = 0
        self.index_last_n = -1
        self.buffer_size = buffer_size
    def write(self, data):
        if not isinstance(data, bytes):
            raise TypeError("Expected bytes, got {}".format(type(data).__name__))
        assert self.index_start < self.buffer_size_current
        assert 0 <= self.index_write < 2 * self.buffer_size_current
        for byte in data:
            if byte == 13:  # ASCII code for '\r'
                # Remove everything after the last '\n'. if no '\n' exists, remove everything.
                # self.buffer = self.buffer[:self.buffer.rfind(b'\n') + 1]
                self.index_write = self.index_last_n + 1
                assert self.index_start <= self.index_write <= self.index_end
                continue
            if byte == 10:
                self.index_last_n = self.index_write
                assert self.index_start <= self.index_last_n <= self.index_write

            self.buffer[self.index_write % self.buffer_size_current] = byte 
            self.index_write += 1
            if self.index_write > self.index_end:
                self.index_end = self.index_write
            if self.index_end >= self.buffer_size_current:
                if self.index_write - self.buffer_size_current >= self.index_start:
                    # buffer is full
                    self.buffer = self.buffer + bytearray(self.buffer_size_current)
                    self.buffer[self.buffer_size_current:self.index_write] = self.buffer[:self.index_write%self.buffer_size_current]
                    self.buffer_size_current = self.buffer_size_current * 2
                    assert self.buffer_size_current == len(self.buffer)

    def write_str(self, data: str):
        self.write(data.encode("utf-8"))
    def getvalue(self):
        return self.buffer
    def get_overflow(self):
        if self.index_end - self.index_start <= self.buffer_size:
            return None
        else:
            overflow_size = self.index_end - self.index_start - self.buffer_size
            overflow_index = self.index_start + overflow_size
            if overflow_index < self.buffer_size_current:
                overflow = self.buffer[self.index_start:overflow_index]
            else:
                overflow = self.buffer[self.index_start:] + self.buffer[:overflow_index % self.buffer_size_current]

            assert self.index_start - 1 <= self.index_last_n < self.index_end
            if self.index_last_n < overflow_index:
                self.index_last_n = overflow_index - 1 
            self.index_start = overflow_index
            assert self.index_end >= self.index_start
            if self.index_start >= self.buffer_size_current:
                self.index_start -= self.buffer_size_current
                self.index_end -= self.buffer_size_current
                self.index_last_n -= self.buffer_size_current
            return overflow
    def get_all(self):
        if self.index_end - self.index_start == 0:
            return None
        else:
            self.index_last_n = self.index_end - 1
            if self.index_end < self.buffer_size_current:
                return self.buffer[self.index_start:self.index_end]
            else:
                return self.buffer[self.index_start:] + self.buffer[:self.index_end % self.buffer_size_current]

class RedirectThreadCR(RedirectThread):
    # CR: \r(carriage return). 
    def __init__(self, parent, buffer_size=65536):
        super().__init__(parent)
        self.buffer_size = buffer_size
        self.buffer = ByteBufferCR()
    def write_output(self, output, f):
        self.buffer.write(output)
        buffer_output = self.buffer.get_overflow()
        if buffer_output is not None:
            f.write(output)
            f.flush() # ensure data is written immediately
        if self.parent.to_stdout:
            try:
                os.write(self.parent.fd_stdout_temp, output)
            except Exception:
                return False
        return True

    def write_buffer_remain(self):
        """write contents remaining in self.buffer"""
        output_remain = self.buffer.get_all()
        if output_remain is not None:
            f = self.f
            f.write(output_remain)
            f.flush()

class RedirectStdOutAndStdErrToFileCR(RedirectStdOutAndStdErrToFile):
    # CR: \r(carriage return). 
    def __init__(self, file_path=None, pipe_previous=None, buffer_size=1024):
        super().__init__(file_path=file_path, pipe_previous=pipe_previous)
        self.buffer_size = buffer_size
    def __enter__(self):
        self.is_terminated = False
        self.thread = RedirectThreadCR(self, buffer_size=self.buffer_size)
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
        self.thread.write_buffer_remain()
        if self.redirect_stderr:
            os.dup2(self.fd_stdout_temp, 1)  # restore stdout to the terminal
            os.close(self.fd_stdout_temp)
        if self.redirect_stdout:
            os.dup2(self.fd_stderr_temp, 2)  # restore stdout to the terminal
            os.close(self.fd_stderr_temp)
        return