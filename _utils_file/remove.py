from _utils_import import _utils_file, shutil
from pathlib import Path
import re

def remove_file(file_path):
    assert _utils_file.file_exist(file_path)
    file_path_obj = Path(file_path)
    file_path_obj.unlink() # missing_ok=False for Python>=3.4
delete_file = remove_file

def remove_file_verbose(file_path, pipe_out=None):
    if pipe_out is None:
        import _utils_io
        pipe_out = _utils_io.PipeOut()
    pipe_out.print("FILE_REMOVE")
    remove_file(file_path)
    with pipe_out.increased_indent():
        pipe_out.print("file_path: %s"%file_path)
delete_file_verbose = remove_file_verbose

def remove_files(*file_path_list):
    for file_path in file_path_list:
        remove_file(file_path)

def remove_dir(dir_path): # remove a folder and all files and child folders in it
    assert _utils_file.dir_exist(dir_path)
    shutil.rmtree(dir_path)
    return
delete_dir = remove_dir

def remove_dir_if_exist(file_path):
    if _utils_file.dir_exist(file_path):
        remove_dir(file_path)

def remove_subdir_if_empty(dir_path_current, recur=True, pipe_out=None):
    def remove_dir_if_empty(dir_path, dir_path_rel, pipe_out=None, **kwargs):
        if _utils_file.is_dir_emtpy(dir_path):
            _utils_file.remove_dir(dir_path)
        if pipe_out is not None:
            pipe_out.print("remove_dir")
            with pipe_out.increased_indent():
                pipe_out.print("DIR_PATH: %s"%dir_path)
    _utils_file.visit_tree(
        dir_path_current=dir_path_current,\
        func=None,
        func_dir=remove_dir_if_empty,
        recur=recur,
        pipe_out=pipe_out
    )
remove_empty_subdir = remove_subdir_if_empty

def clear_dir(dir_path):
    # remove all files and subfolders in folder
    if _utils_file.dir_exist(dir_path):
        try:
            _utils_file.remove_dir(dir_path)
            _utils_file.create_dir(dir_path)
        except Exception: # failed to remove dir
            for file_path in _utils_file.list_all_file_path(dir_path):
                _utils_file.remove_file(file_path)
            for dir_path in _utils_file.list_all_dir_path(dir_path):
                _utils_file.remove_dir(file_path)
    else:
        _utils_file.create_dir(dir_path)
    assert _utils_file.dir_exist(dir_path)

def remove_file_if_exist(file_path):
    if _utils_file.file_exist(file_path):
        remove_file(file_path)

def remove_file_with_suffix(dir_path: str, suffix: str):
    dir_path = _utils_file.check_dir_exist(dir_path)
    suffix = suffix.lstrip(".")
    for file_path in _utils_file.list_all_file_path(dir_path): 
        file_path_no_suffix, _suffix = _utils_file.get_file_name_and_suffix(dir_path)
        if _suffix == suffix:
            remove_file(file_path)

def remove_file_if_has_suffix(dir_path, suffix):
    suffix = suffix.lstrip(".")
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    for file_name in _utils_file.list_all_file_name(dir_path):
        _, _suffix = _utils_file.get_file_name_and_suffix(file_name)
        if _suffix is not None:
            if _suffix == suffix:
                _utils_file.remove_file(dir_path + file_name)

def remove_dir_if_is_empty(dir_path: str):
    if _utils_file.is_dir_emtpy(dir_path):
        _utils_file.remove_dir(dir_path)
        return True
    else:
        return False

def remove_file_if_name_match_pattern(dir_path, pattern=None,):
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    pattern_compiled = re.compile(pattern)
    for file_name in _utils_file.list_all_file_name(dir_path):
        if pattern_compiled.match(file_name) is not None:
            _utils_file.remove_file(dir_path + file_name)

def remove_dir_if_name_match_pattern(dir_path, pattern=None):
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    pattern_compiled = re.compile(pattern)
    for dir_name in _utils_file.list_all_file_name(dir_path):
        if pattern_compiled.match(dir_name) is not None:
            _utils_file.remove_file(dir_path + dir_name)