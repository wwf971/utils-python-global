from __future__ import annotations
import os, re
from pathlib import Path
from _utils_import import _utils, pickle, Dict
import _utils_file
from .path import (
    dir_path_to_unix_style,
    file_path_to_unix_style,
    dir_path_to_win_style,
    get_dir_name_of_dir_path,
    get_dir_path_of_dir_path, get_parent_dir_path,
    get_file_name_of_file_path, get_dir_path_of_file_path,
    get_file_name_and_suffix,
    get_file_path_and_suffix,
    get_file_name_suffix,
    get_file_path_suffix,
    get_file_suffix,
    is_equiv_file_path,
    get_dir_path_current,
    get_dir_path_parent,
    get_file_path_current,
    get_file_path_current_no_suffix,
    change_file_path_current_suffix
)

def is_file_path(file_path: str):
    if file_path.endswith("/"):
        return False
    return True

def check_is_file_path(file_path: str):
    assert is_file_path(file_path)

def file_exist(file_path):
    # if path ends with "/" or "\\", file_exist(path) should always return False 
    if "~" in file_path:
        return Path(os.path.expanduser(file_path)).is_file()
    return Path(file_path).is_file()

def files_exist(*file_path_list):
    for file_path in file_path_list:
        if not file_exist(file_path):
            return False
    return True

def check_file_exist(file_path):
    assert file_exist(file_path), file_path
    return file_path

def check_files_exist(*file_path_list):
    for file_path in file_path_list:
        check_file_exist(file_path)

def check_file_path_suffix(file_path, suffix):
    _suffix = get_file_path_suffix(file_path)
    assert suffix == _suffix
check_file_suffix = check_file_path_suffix

def dir_exist(dir_path):
    return Path(dir_path).is_dir()

def check_dir_exist(dir_path):
    assert dir_exist(dir_path)
    return dir_path

def path_exist(path:str):
    return file_exist(path) or path_exist(path)

def change_file_path_if_exist(file_path: str):
    check_is_file_path(file_path)
    if not file_exist(file_path):
        return file_path

    file_path_no_suffix, suffix = get_file_path_and_suffix(file_path)
    dir_path_parent = get_dir_path_of_file_path(file_path) # end with "/"

    index = 0
    
    # TODO: file_name already in form of xxx-0.yy
    # match_result = re.match(r"^(.*)-(\d+)$", file_path_no_suffix)
    while True:
        file_path_new = file_path_no_suffix + "-%d"%index + "." + suffix
        if not (file_exist(file_path_new) or dir_exist(file_path_new)):
            # linux/windows/macos/(most os) does not allow file and folder with same name in one folder.
            break
        index += 1
    assert not file_exist(file_path_new)
    return file_path_new

def to_absolute_dir_path(dir_path):
    if "~" in dir_path:
        dir_path = os.path.expanduser(dir_path)
    return os.path.abspath(dir_path) + "/"

def get_all_file_name(dir_path):
    file_name_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    return file_name_list

def list_all_file_name(dir_path):
    for f in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, f)):
            yield f

def list_all_file_path(dir_path, recur=False):
    if recur:
        return list_all_file_path_in_tree(dir_path, order="depth_first")
    if not dir_path.endswith("/") or dir_path.endswith("\\"):
        dir_path += "/"
    return [dir_path + file_name for file_name in list_all_file_name(dir_path)]

def list_all_file_name_and_path(dir_path, recur=False):
    if recur:
        return list_all_file_path_in_tree(dir_path, order="depth_first")
    if not dir_path.endswith("/") or dir_path.endswith("\\"):
        dir_path += "/"
    return [(file_name, dir_path + file_name) for file_name in list_all_file_name(dir_path)]

def list_all_file_name_with_name_pattern(dir_path, pattern: str, recur=False, _yield=True):
    if recur:
        raise NotImplementedError
    pattern_compiled = re.compile(pattern)
    dir_path = dir_path_to_unix_style(dir_path)

    if _yield:
        for file_name in list_all_file_path(dir_path):
            if pattern_compiled.match(file_name) is None:
                yield file_name
    else:
        file_name_list = []
        for file_name in list_all_file_path(dir_path):
            if pattern_compiled.match(file_name) is None:
                file_name_list.append(file_name)
        return file_name_list
list_all_file_name_with_pattern = list_all_file_name_with_name_pattern

def list_all_file_path_with_name_pattern(dir_path, pattern: str, recur=False, _yield=True):
    if recur:
        raise NotImplementedError
    pattern_compiled = re.compile(pattern)
    dir_path = dir_path_to_unix_style(dir_path)

    if _yield:
        for file_name in list_all_file_path(dir_path):
            if pattern_compiled.match(file_name) is None:
                yield file_name
    else:
        file_name_list = []
        for file_name in list_all_file_path(dir_path):
            if pattern_compiled.match(file_name) is None:
                file_name_list.append(file_name)
        return file_name_list

from collections import deque
def list_all_file_path_in_tree(dir_path, order="depth_first"):
    order = order.lower()
    if order in ["depth_first"]:
        get_dir_path_next = lambda dir_path_list: dir_path_list.pop()
    elif order in ["breadth_first"]:
        get_dir_path_next = lambda dir_path_list: dir_path_list.popleft()
    else:
        raise ValueError(order)

    dir_path = _utils_file.check_file_exist(dir_path)
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    dir_path_list = deque([dir_path])

    while len(dir_path_list) > 0:
        dir_path_current = get_dir_path_next(dir_path_list)
        for file_name in _utils_file.list_all_file_name(dir_path_current):
            yield dir_path_current + file_name
        for dir_name in _utils_file.list_all_dir_name(dir_path_current):
            dir_path_list.append(dir_path_current + dir_name + "/")

def list_all_dir_name(dir_path, _yield=True):
    if _yield:
        for f in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, f)):
                yield f + "/" 
    else:
        dir_name_list = [f + "/" for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
        return dir_name_list

def list_all_dir_path(dir_path, _yield=True):
    if _yield:
        for f in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, f)):
                yield dir_path + "/" + f + "/" 
    else:  
        dir_path = dir_path_to_unix_style(dir_path)
        dir_path_list = [dir_path + "/" + f + "/" for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
        return dir_path_list

def list_all_dir_name_and_path(dir_path, _yield=True):
    if _yield:
        for f in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, f)):
                yield (f + "/", dir_path + "/" + f + "/")
    else:  
        dir_path = dir_path_to_unix_style(dir_path)
        dir_path_list = [(f + "/", dir_path + "/" + f + "/") for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
        return dir_path_list

def is_dir_emtpy(dir_path):
    return not any(Path(dir_path).iterdir())

def list_all_file_name_with_suffix(dir_path: str, suffix: str):
    file_name_list = []
    suffix = suffix.lstrip(".")
    for file_name in list_all_file_name(dir_path):
        _, _suffix = get_file_name_and_suffix(file_name)
        if _suffix == suffix:
            file_name_list.append(file_name)
    return file_name_list

def list_all_file_path_with_suffix(dir_path: str, suffix: str):
    file_path_list = []
    suffix = suffix.lstrip(".")
    for file_name, file_path in list_all_file_name_and_path(dir_path):
        _, _suffix = get_file_name_and_suffix(file_name)
        if _suffix == suffix:
            file_path_list.append(file_path)
    return file_path_list

def visit_tree(dir_path_current, func=None, recur=True, verbose=False, dir_path_rel=None, func_dir=None, **kwargs):
    if dir_path_rel is None: # root
        dir_path_current = check_dir_exist(dir_path_current)
        dir_path_current = dir_path_to_unix_style(dir_path_current)
        dir_path_rel = ""
    if verbose:
        print(dir_path_current)
    if func is not None:
        for file_name in list_all_file_name(dir_path_current):
            func(
                dir_path_current=dir_path_current,
                file_name=file_name,
                dir_path_rel=dir_path_rel,
                **kwargs
            )
    if recur:
        for dir_name in list_all_dir_name(dir_path_current):
            visit_tree(
                dir_path_current=dir_path_current + dir_name, func=func,
                dir_path_rel=dir_path_rel + dir_name, # dir_name ends with "/"
                **kwargs
            )
            if func_dir is not None:
                func_dir(
                    dir_path=dir_path_current + dir_name,
                    dir_path_rel=dir_path_rel + dir_name,
                    **kwargs
                )

def create_file(file_path: str):
    assert not file_exist(file_path)
    with open(file_path, 'w') as file:
        pass  # This creates an empty file
    return
create_empty_file = create_file

def create_dir(dir_path):
    dir_path_obj = Path(dir_path)
    dir_path_obj.mkdir(parents=True, exist_ok=True)
    return dir_path_obj.__str__() + "/"
create_dir_if_not_exist = create_dir

def create_dir_for_file_path(file_path):
    dir_path_obj = Path(file_path).parent
    dir_path_obj.mkdir(parents=True, exist_ok=True)
    return file_path

def get_file_path_no_suffix(file_path):
    file_path_no_suffix, suffix = get_file_name_and_suffix(file_path)
    return file_path_no_suffix

def change_file_path_suffix(file_path:str, suffix:str):
    suffix = suffix.lstrip(".")
    file_path_no_suffix, _suffix = get_file_name_and_suffix(file_path)
    assert _suffix is not None
    file_path_new = file_path_no_suffix + "." + suffix
    return file_path_new

def change_file_name_suffix(file_name:str, suffix:str):
    return change_file_name_suffix(file_path=file_name, suffix=suffix)

def to_file(obj, file_path):
    file_path = create_dir_for_file_path(file_path)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)

def from_file(file_path):
    file_path = check_file_exist(file_path)    
    with open(file_path, 'rb') as f:
        obj = pickle.load(f, encoding='bytes')
    return obj

def get_file_create_unix_stamp(file_path):
    import _utils_system
    file_path = check_file_exist(file_path)
    if _utils_system.is_win():
        unix_stamp_create = os.path.getctime(file_path) # create_time
    elif _utils_system.is_linux() or _utils_system.is_macos():
        # https://stackoverflow.com/questions/237079
        stat = os.stat(file_path)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime
    else:
        raise NotImplementedError
    return unix_stamp_create

def get_file_latest_create(dir_path: str):
    file_path_list = _utils_file.list_all_file_path(dir_path)
    if len(file_path_list) == 0:
        return None
    return get_file_latest_create_from_file_list(file_path_list)

def get_file_latest_create_from_file_list(file_path_list):
    file_path_latest = None
    time_stamp_latest = None
    for file_path in file_path_list:
        time_stamp_create = _utils_file.get_file_create_unix_stamp(file_path)
        if time_stamp_latest is None or time_stamp_latest < time_stamp_create:
            time_stamp_latest = time_stamp_create
            file_path_latest = file_path
    return file_path_latest 

def get_file_modify_unix_stamp(file_path): # last modified time
    file_path = check_file_exist(file_path)
    # os.path.getmtime is robust across platform and file system
    unix_stamp_modify = os.path.getmtime(file_path) # last modified time
    return unix_stamp_modify
get_file_last_modify_time = get_file_modify_unix_stamp

def get_dir_config(dir_path, recur=True):
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    config = Dict(files=Dict(), dirs=Dict())
    for file_name, file_path in _utils_file.list_all_file_name_and_path(dir_path):
        size = _utils_file.get_file_size(file_path)
        size_str = _utils.byte_num_to_size_str(size)
        config.files[file_name] = Dict(
            md5=_utils_file.get_file_md5(file_path),
            size=size, size_str=size_str
        )
    if recur:
        for dir_name, _dir_path in _utils_file.list_all_dir_name_and_path(dir_path):
            config.dirs[dir_name] = get_dir_config(_dir_path)
    else:
        for dir_name, _dir_path in _utils_file.list_all_dir_name_and_path(dir_path):
            config.dirs[dir_name] = "__recur=false__"
    
    return config

def check_dir_config(dir_path, config: Dict):
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    for file_name, file_config in config.files.items():
        file_path = dir_path + file_name
        if not _utils_file.file_exist(file_path):
            return False
        size = _utils_file.get_file_byte_num(file_path)
        if size != file_config.size:
            return False
        md5 = _utils_file.get_file_md5(file_path)
        if md5 != file_config.md5:
            return False
    
    for dir_name, dir_config in config.dirs.items():
        _dir_path = dir_path + dir_name
        if not _utils_file.dir_exist(_dir_path):
            return False
        if isinstance(dir_config, str):
            continue
        if not check_dir_config(_dir_path, dir_config):
            return False
    return True

def obj_to_binary_file(obj, file_path):
    _utils_file.create_dir_for_file_path(file_path)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)

def binary_file_to_obj(file_path):
    _utils_file.check_file_exist(file_path)
    with open(file_path, 'rb') as f:
        obj = pickle.load(f, encoding='bytes')
    return obj

def natural_sort(file_name_list, _nsre=None)->list:
    if _nsre is None:
        _nsre = re.compile(r'(\d+)')
    def to_key(file_name):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(file_name)
        ]
    return sorted(file_name_list, key=to_key)

import _utils_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _utils_io import (
        text_file_to_str,
        str_to_text_file,
    )
    from _utils import (
        to_yaml_file,
        from_yaml_file,
        dict_to_json_file,
        json_str_to_dict
    )
else:
    text_file_to_str = _utils_import.lazy_from_import("_utils_io", "text_file_to_str")
    str_to_text_file = _utils_import.lazy_from_import("_utils_io", "str_to_text_file")
    to_yaml_file = _utils_import.lazy_from_import("_utils", "to_yaml_file")
    from_yaml_file = _utils_import.lazy_from_import("_utils", "from_yaml_file")
    dict_to_json_file = _utils_import.lazy_from_import("_utils", "dict_to_json_file")
    json_str_to_dict = _utils_import.lazy_from_import("_utils", "json_str_to_dict")

from .move import (
    move_file, copy_file, rename_file,
    move_file_overwrite,
    move_if_file_name_match_pattern,
)

from .remove import (
    remove_file, remove_files,
    remove_dir,
    remove_dir_if_exist,
    clear_dir,
    remove_subdir_if_empty,
    remove_dir_if_is_empty,
    remove_file_if_exist,
    remove_file_with_suffix, remove_file_if_has_suffix,
    remove_dir_if_is_empty,
    remove_file_if_name_match_pattern,
    remove_dir_if_name_match_pattern,   
)
delete_file = remove_file
delete_files = remove_files
delete_dir = remove_dir
delete_dir_if_exist = remove_dir_if_exist

from .content import (
    get_file_byte_num, get_file_size,
    get_file_size_str,
    get_file_md5,
    have_same_content
)

from .zip import (
    is_zip_file,
    extract_zip_file,
)

from ._gzip import (
    is_gz_file,
    extract_gz_file,
)

from .user import get_user_download_folder