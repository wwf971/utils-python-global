
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

from file_io_cr import ByteBufferCR
from _utils_import import _utils_file, _utils_io

file_path_stdout = _utils_file.get_file_path_current_no_suffix(__file__) + "~stdout.log"
file_path_stderr = _utils_file.get_file_path_current_no_suffix(__file__) + "~stderr.log"

import time
def child_func(num = 0, *args, **kwargs):
    _num = 0
    while _num < 5:
        print("child: %s --> sys.stdout"%num, file=sys.stdout)
        print("child: %s --> sys.stderr"%num, file=sys.stderr)
        print("child: %s --> sys.__stdout__"%num, file=sys.__stdout__)
        print("child: %s --> sys.__stderr__"%num, file=sys.__stderr__)
        time.sleep(1)
        num += 1
        _num += 1


from _utils import get_random_str
import random, string
def get_random_str_cr(length):
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
    test_str = get_random_str(length)
    
    index_list = [0] + get_index(10, length) + [length]
    buf = ByteBufferCR(buf_size=5)
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
    test_str = get_random_str_cr(length)
    truth_str = get_truth_str(test_str)
    
    index_list = [0] + get_index(10, length) + [length]
    buf = ByteBufferCR(buf_size=length)
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

    return True

def unit_test_3():
    import _utils_file
    def func():
        from tqdm import tqdm
        import time
        total = 100
        for i in tqdm(range(total)):
            time.sleep(0.01)  # Simulate work
    
    file_path_stdout = _utils_file.get_file_path_no_suffix(__file__) + "~stdout~3.txt"
    _utils_io.run_func_with_output_to_file_dup_cr(
        func,
        file_path_stdout=file_path_stdout
    )

    str_output = _utils_file.text_file_to_str(file_path_stdout)
    import re
    result = re.match(r"100%\|██████████\| 100/100 \[00:01<00:00, (\d{2}).(\d{2})it/s\]\n", str_output)
    print("%s:%s"%(result.group(1), result.group(2)))
    return True

if __name__ == "__main__":
    unit_test_1()
    unit_test_2()
    unit_test_3()
    pass
    _utils_io.run_func_with_output_to_file_dup_cr(
        child_func,
        file_path_stdout=file_path_stdout,
        file_path_stderr=file_path_stderr,
        print_to_stdout=False
    )
    child_func(num=6)

    sys.exit(0)

