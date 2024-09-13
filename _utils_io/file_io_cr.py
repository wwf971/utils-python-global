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
class BytesBufferCR:
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
    def __init__(self, parent, buffer_size=65536):
        super().__init__(parent)
        self.buffer_size = buffer_size
        self.buffer = BytesBufferCR()
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

import string, random
def get_random_string(length):
    letters = string.ascii_letters  # Use letters from 'a-z', 'A-Z'
    return ''.join(random.choice(letters) for _ in range(length))

def get_random_string_cr(length):
    letters = string.ascii_letters + "\n\r"  # Use letters from 'a-z', 'A-Z'
    return ''.join(random.choice(letters) for _ in range(length))

def get_index(n, range_max):
    # Randomly sample unique integers
    random_integers = random.sample(range(range_max), n)
    # Sort the integers
    return sorted(random_integers)

def get_truth_str(test_str):
    output_str = ["*" for _ in range(len(test_str) + 3)]
    last_n_index = -1
    index = 0
    for c in test_str:
        if c == "\r":
            index = last_n_index + 1
            continue
        elif c == "\n":
            last_n_index = index
        output_str[index] = c
        index += 1
    
    for index in range(len(output_str)):
        if output_str[index] == "*":
            return "".join(output_str[:index])

def unit_test_1():
    length = 1000
    test_str = get_random_string(length)
    
    index_list = [0] + get_index(10, length) + [length]
    buf = BytesBufferCR(buffer_size=5)
    overflow_list = []
    for _ in range(len(index_list) - 1):
        buf.write_str(test_str[index_list[_]:index_list[_+1]])
        overflow = buf.get_overflow()
        if overflow is not None:
            overflow_list.append(overflow)    
    overflow_list.append(buf.get_all())
    output_str = "".join([_.decode("utf-8") for _ in overflow_list])
    assert output_str == test_str

def unit_test_2():
    length = 1000
    test_str = get_random_string_cr(length)
    # test_str = 'gdeSduZsa\rfweqUQJQPicmYfKWQRvmRtIoDmFoHHzixfnL\roAMJVTUQXlJvKeIeMvtgybiMdTtIeixQBHS\rTIBSzHmaLhyTDcMbN\newB\nhhdoGSTDd\rUz\rGjDdybjXOprglZMxbGewRhokSK\ndTJWJqnYWlxqKbXlvmErbCUFZhzduarbRYTxEgbTzDsgojiblyXrvSfqV\rwpHKLGxM\rXTnfuSUfKbkmlVxcuQJInjnZXIYoEpwvRHJsSbgThOljXygOaZLpfrzlXLMFilX\nMTzlzhFSirperkjLXpighhkXPwcSE\ndo\nwYyGVPJOa\rNEravhyqDUUviGUJGUtKHylZpKElwOeSWRLzUeZdfUVovHrCHPywLirhicRehpDotpRoXxZwuMgy\rvrvgo\rzqxKXZGN\noGuFeUqxbxbMdlQTpbRmCpjPdDHxemKrDEnBqbRUO\rKpqlQvQezvvpiudunbFKAZVZqPCJv\rgJESliKcGzmltgAgNJrhMviDTLuhjLw\nzwRs\rewGqhHDbpDijZtXngYoVujPJXSSSzvnTeMB\rFcQsmAWLGosFOyWxdqHSOQYOkqWrJECwNmnPovfYSDY\rjbmutCrbAiFevtNVyapzjkyjaLUZjtkZZ\riocFCXRefLFoXHVjCn\nGmNYHZmheWfxmoRQZuCWKgHaSBQMlyIuglnWAoJSvNGnbQHBcP\namPLnmCCJAtaIq\rgUs\nUgApluyWJIWpQ\rTHbULzyqhuLmdbCMzUNItMhAdgtInIF\rLfHIKGP\nGhpHLKlVjSTdrbsCoBOBDDRRUf\rXcBWEupTOKTQCedGMChUFMUzkKKZIjxrgTzDEgmWXAMiB\rBwyBgFrRvX\rcYocgIxWLUUWVVSUGlD\nwbvgvljxmazMrpUnCebzqTRsAteDsQSAXlYdAkyNQWyp\rBFqz\rtCUNPbecroTjaXTYajL\rGbGkrWpJreAGUsIxYmrxaKRNyGEuzqilGZEdepxEwBpiEwzqQ'
    truth_str = get_truth_str(test_str)
    
    index_list = [0] + get_index(10, length) + [length]
    buf = BytesBufferCR(buffer_size=length)
        # if buffer_size is too small, some \r could not go back to last \n, as last \n has been flushed.
    overflow_list = []
    for _ in range(len(index_list) - 1):
        buf.write_str(test_str[index_list[_]:index_list[_+1]])
        overflow = buf.get_overflow()
        if overflow is not None:
            overflow_list.append(overflow)    
    overflow_list.append(buf.get_all())
    output_str = "".join([_.decode("utf-8") for _ in overflow_list])
    assert output_str == truth_str

    return

def unit_test_3():
    import _utils_file
    save_file_path = _utils_file.get_file_path_without_suffix(__file__) + "-stdout.txt"
    with RedirectStdOutAndStdErrToFileCR(file_path=save_file_path):
        from tqdm import tqdm
        import time

        total = 100
        for i in tqdm(range(total)):
            time.sleep(0.01)  # Simulate work


    save_str = _utils_file.text_file_to_str(save_file_path)
    import re
    result = re.match(r"100%\|██████████\| 100/100 \[00:01<00:00, (\d{2}).(\d{2})it/s\]\n", save_str)
    
    print("%s:%s"%(result.group(1), result.group(2)))
    return

if __name__ == "__main__":
    unit_test_1()
    unit_test_2()
    unit_test_3()