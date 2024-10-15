
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

from _utils_io.file_io_cr import (
    ByteBufferCR,
    RedirectStdOutAndStdErrToFile,
    RedirectStdOutAndStdErrToFileCR
)

from _utils import get_random_string
import random, string
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
    buf = ByteBufferCR(buffer_size=5)
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
    buf = ByteBufferCR(buffer_size=length)
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
    save_file_path = _utils_file.get_file_path_no_suffix(__file__) + "-stdout.txt"
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
    return True

if __name__ == "__main__":
    unit_test_1()
    unit_test_2()
    unit_test_3()
    pass