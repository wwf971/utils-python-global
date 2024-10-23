
from _utils_import import _utils_file, _utils_system
import sys, os, traceback
import _utils_io
from io import StringIO, BytesIO
class BytesBufCR:
    # byte buffer that deals with CR(carriage return) just like in terminals
    def __init__(self, buf_size=65536):
        self.buf = bytearray(1024)
        self.buf_size_current = len(self.buf)
        self.index_start = 0
        self.index_write = 0
        self.index_end = 0
        self.index_last_n = -1
        self.buf_size = buf_size
    def write(self, data):
        if not isinstance(data, bytes):
            raise TypeError("Expected bytes, got {}".format(type(data).__name__))
        assert self.index_start < self.buf_size_current
        assert 0 <= self.index_write < 2 * self.buf_size_current
        for byte in data:
            if byte == 13:  # ASCII code for '\r'
                # Remove everything after the last '\n'. if no '\n' exists, remove everything.
                # self.buf = self.buf[:self.buf.rfind(b'\n') + 1]
                self.index_write = self.index_last_n + 1
                assert self.index_start <= self.index_write <= self.index_end
                continue
            if byte == 10:
                self.index_last_n = self.index_write
                assert self.index_start <= self.index_last_n <= self.index_write

            self.buf[self.index_write % self.buf_size_current] = byte 
            self.index_write += 1
            if self.index_write > self.index_end:
                self.index_end = self.index_write
            if self.index_end >= self.buf_size_current:
                if self.index_write - self.buf_size_current >= self.index_start:
                    # buf is full
                    self.buf = self.buf + bytearray(self.buf_size_current)
                    self.buf[self.buf_size_current:self.index_write] = self.buf[:self.index_write%self.buf_size_current]
                    self.buf_size_current = self.buf_size_current * 2
                    assert self.buf_size_current == len(self.buf)
    def write_str(self, data: str):
        self.write(data.encode("utf-8"))
    def getvalue(self):
        return self.buf
    def get_overflow(self):
        if self.index_end - self.index_start <= self.buf_size:
            return None
        else:
            overflow_size = self.index_end - self.index_start - self.buf_size
            overflow_index = self.index_start + overflow_size
            if overflow_index < self.buf_size_current:
                overflow = self.buf[self.index_start:overflow_index]
            else:
                overflow = self.buf[self.index_start:] + self.buf[:overflow_index % self.buf_size_current]
            assert self.index_start - 1 <= self.index_last_n < self.index_end
            if self.index_last_n < overflow_index:
                self.index_last_n = overflow_index - 1 
            self.index_start = overflow_index
            assert self.index_end >= self.index_start
            if self.index_start >= self.buf_size_current:
                self.index_start -= self.buf_size_current
                self.index_end -= self.buf_size_current
                self.index_last_n -= self.buf_size_current
            return overflow
    def get_all(self):
        if self.index_end - self.index_start == 0:
            return None
        else:
            self.index_last_n = self.index_end - 1
            if self.index_end < self.buf_size_current:
                return self.buf[self.index_start:self.index_end]
            else:
                return self.buf[self.index_start:] + self.buf[:self.index_end % self.buf_size_current]

def run_func_with_output_to_file_dup_cr(func, file_path_stdout, *args, file_path_stderr=None, pipe_prev=None, print_to_stdout=False, **kwargs):
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

    def listen_thread(fd_read, file_path, buf:BytesBufCR, pipe_prev=None):
        with open(file_path, "wb") as f:
            if pipe_prev is not None:
                if isinstance(pipe_prev, BytesIO):
                    out_bytes = _utils_io.read_from_string_io(pipe_prev.buf)
                else:
                    pass # TODO
                buf.write(out_bytes)
                out_bytes = buf.get_overflow()
                if out_bytes is not None:
                    print_bytes_to_f(out_bytes, f)

            while True:
                out_bytes = os.read(fd_read, 1024)  # fd_read --> f
                buf.write(out_bytes)
                out_bytes = buf.get_overflow()
                if out_bytes is not None:
                    if not print_bytes_to_f(out_bytes, f): break
                    if not print_bytes_to_stdout(out_bytes): break
    
    def write_buf_remain(buf: BytesBufCR, file_path):
        with open(file_path, "wb") as f:
            out_bytes = buf.get_all()
            if out_bytes is not None:
                if not print_bytes_to_f(out_bytes, f): return
                if not print_bytes_to_stdout(out_bytes): return

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
        buf = BytesBufCR()
        _listen_thread = _utils_system.start_thread(
            listen_thread, fd_read=fd_read, file_path=file_path_stdout, pipe_prev=pipe_prev,
            buf=buf,
            dependent=True, join=False
        )
    else:
        buf_stdout = BytesBufCR()
        buf_stderr = BytesBufCR()
        _listen_thread_stdout = _utils_system.start_thread(
            listen_thread, fd_read=fd_read_stdout, file_path=file_path_stdout, pipe_prev=pipe_prev,
            buf=buf_stdout,
            dependent=True, join=False
        )
        _listen_thread_stderr = _utils_system.start_thread(
            listen_thread, fd_read=fd_read_stderr, file_path=file_path_stderr, pipe_prev=pipe_prev,
            buf=buf_stderr,
            dependent=True, join=False
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
        write_buf_remain(buf, file_path_stdout)
    else:
        _listen_thread_stdout.join(0.2)
        _listen_thread_stderr.join(0.2)
        write_buf_remain(buf_stdout, file_path_stdout)
        write_buf_remain(buf_stderr, file_path_stderr)

    # restore
    os.dup2(fd_stdout_origin, 1) # restore stdout to the terminal
    os.close(fd_stdout_origin)
    os.dup2(fd_stderr_origin, 2) # restore stdout to the terminal
    os.close(fd_stderr_origin)
    return