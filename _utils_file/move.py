

from _utils_import import _utils_file
import re

from pathlib import Path
from _utils_import import shutil

def move_file(file_path_source, file_path_target):
    assert _utils_file.file_exist(file_path_source)
    assert not _utils_file.file_exist(file_path_target)
    _utils_file.create_dir_for_file_path(file_path_target)
    shutil.move(file_path_source, file_path_target)
    # Path(file_path_source).rename(file_path_target)
        # [WinError 17] 系统无法将文件移到不同的磁盘驱动器。
    assert not _utils_file.file_exist(file_path_source)
    assert _utils_file.file_exist(file_path_target)

def copy_file(file_path_source, file_path_target):
    assert _utils_file.file_exist(file_path_source)
    _utils_file.create_dir_for_file_path(file_path_target)
    shutil.copy2(file_path_source, file_path_target) # copy2() preseves timestamp. copy() does not.
    assert _utils_file.file_exist(file_path_target)
    return

def rename_file(dir_path, file_name, file_name_new):
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    file_path = dir_path + file_name
    file_path_new = dir_path + file_name_new
    move_file(file_path, file_path_new)

def move_file_overwrite(file_path_source, file_path_target):
    assert _utils_file.file_exist(file_path_source)
    Path(file_path_source).rename(file_path_target)
    assert not _utils_file.file_exist(file_path_source)
    assert _utils_file.file_exist(file_path_target)

def move_if_file_name_match_pattern(
    dir_path,
    dir_path_target,
    pattern=None,
):
    pattern_compiled = re.compile(pattern)
    dir_path_target = _utils_file.dir_path_to_unix_style(dir_path)
    for file_name in _utils_file.list_all_file_name(dir_path):
        if pattern_compiled.match(file_name) is not None:
            _utils_file.move_file(dir_path + file_name, dir_path_target + file_name)