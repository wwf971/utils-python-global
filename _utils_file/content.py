
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

def files_have_same_content(file_path_1, file_path_2):
    _utils_file.check_file_exist(file_path_1)
    _utils_file.check_file_exist(file_path_2)

    byte_num_1 = get_file_byte_num(file_path_1)
    byte_num_2 = get_file_byte_num(file_path_2)
    if byte_num_1 != byte_num_2:
        return False

    import filecmp # python standard lib
    is_same_content = filecmp.cmp(file_path_1, file_path_2, shallow=False) # byte to byte comparison
    return is_same_content
have_same_content = files_have_same_content

def dirs_have_same_content(dir_path_1, dir_path_2):
    dir_path_1 = _utils_file.dir_path_to_unix_style(dir_path_1)
    dir_path_2 = _utils_file.dir_path_to_unix_style(dir_path_2)
    return _dirs_have_same_content(dir_path_1, dir_path_2)

def _dirs_have_same_content(dir_path_1, dir_path_2):
    file_list_1 = list(_utils_file.list_all_file_name(dir_path_1))
    file_list_2 = list(_utils_file.list_all_file_name(dir_path_2))
    if not len(list(file_list_1)) == len(list(file_list_2)):
        return False

    for file_name in file_list_1:
        file_path_1 = dir_path_1 + file_name
        file_path_2 = dir_path_2 + file_name
        if not _utils_file.file_exist(file_path_2):
            return False
        if not _utils_file.have_same_content(file_path_1, file_path_2):
            return False
    
    dir_list_1 = list(_utils_file.list_all_dir_name(dir_path_1))
    dir_list_2 = list(_utils_file.list_all_dir_name(dir_path_2))
    if not len(list(dir_list_1)) == len(list(dir_list_2)):
        return False

    for subdir_name in dir_list_1:
        subdir_path_1 = dir_path_1 + subdir_name
        subdir_path_2 = dir_path_2 + subdir_name
        if not _utils_file.dir_exist(subdir_path_2):
            return False
        if not _dirs_have_same_content(subdir_path_1, subdir_path_2):
            return False

    return True

def get_file_md5(file_path) -> str:
    import hashlib
    md5_calculator = hashlib.md5()
    _utils_file.check_file_exist(file_path)
    with open(file_path, 'rb') as f:
        bytes = f.read()
    md5_calculator.update(bytes)
    md5_str = md5_calculator.hexdigest()
    return md5_str
