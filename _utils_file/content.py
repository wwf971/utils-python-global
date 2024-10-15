
from _utils_import import _utils_file
import os

def get_file_byte_num(file_path: str) -> int:
    _utils_file.check_file_exist(file_path)
    byte_num = os.path.getsize(file_path)
    return byte_num
get_file_size = get_file_byte_num

def get_file_size_str(file_path: str):
    byte_num = get_file_byte_num(file_path)
    from _utils import byte_num_to_size_str
    size_str = byte_num_to_size_str(byte_num)
    return size_str

def have_same_content(file_path_1, file_path_2):
    _utils_file.check_file_exist(file_path_1)
    _utils_file.heck_file_exist(file_path_2)

    byte_num_1 = get_file_byte_num(file_path_1)
    byte_num_2 = get_file_byte_num(file_path_2)
    if byte_num_1 != byte_num_2:
        return False

    import filecmp # python standard lib
    is_same_content = filecmp.cmp(file_path_1, file_path_2, shallow=False) # byte to byte comparison
    return is_same_content

def get_file_md5(file_path) -> str:
    import hashlib
    md5_calculator = hashlib.md5()
    _utils_file.check_file_exist(file_path)
    with open(file_path, 'rb') as f:
        bytes = f.read()
    md5_calculator.update(bytes)
    md5_str = md5_calculator.hexdigest()
    return md5_str
