import os
from pathlib import Path
from _utils_import import pickle, shutil, _utils_file

def get_dir_path_current(__file__: str):    
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    return dir_path_current

def get_dir_path_parent(__file__: str):    
    dir_path_parent = os.path.dirname(os.path.realpath(__file__)) + "/"
    return dir_path_parent

def file_path_to_unix_style(file_path: str):
    # TODO: handle ~ in file path
    dir_path = dir_path.replace("\\", "/")
    return file_path

def dir_path_to_unix_style(dir_path: str):
    # TODO: handle ~ in dir path
    dir_path = dir_path.replace("\\", "/")
    dir_path = dir_path.rstrip("/")
    dir_path += "/"
    return dir_path

def is_file_path(file_path: str):
    if file_path.endswith("/"):
        return False
    return

def check_is_file_path(file_path: str):
    assert is_file_path(file_path)

def file_exist(file_path):
    # if path ends with "/" or "\\", file_exist(path) should always return False 
    return Path(file_path).is_file()

def check_file_exist(file_path):
    assert file_exist(file_path)
    return file_path

def is_same_file(file_path_1, file_path_2):
    return os.path.samefile(file_path_1, file_path_2)

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
        file_path_new = dir_path_parent + file_path_no_suffix + "-%d"%index + "." + suffix
        if not (file_exist(file_path_new) or dir_exist(file_path_new)):
            # linux/windows/macos/(most os) does not allow file and folder with same name in one folder.
            return file_path_new

def list_all_file_name(dir_path):
    file_name_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    return file_name_list

def list_all_dir_name(dir_path):
    dir_name_list = [f + "/" for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
    return dir_name_list

def list_all_dir_path(dir_path):
    dir_path = dir_path_to_unix_style(dir_path)
    dir_path_list = [dir_path + "/" + subdir_name + "/" for subdir_name in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
    return dir_path_list

def list_all_file_path(dir_path):
    if not dir_path.endswith("/") or dir_path.endswith("\\"):
        dir_path += "/"
    return [dir_path + file_name for file_name in list_all_file_name(dir_path)]

def visit_tree(dir_path_current, func, recur=True, verbose=False, dir_path_rel=None, **kwargs):
    if dir_path_rel is None: # root
        dir_path_current = check_dir_exist(dir_path_current)
        dir_path_rel = ""
    if verbose:
        print(dir_path_current)
    for file_name in list_all_file_name(dir_path_current):
        func(dir_path_current=dir_path_current, file_name=file_name, dir_path_rel=dir_path_rel, **kwargs)
    if recur:
        for dir_name in list_all_dir_name(dir_path_current):
            visit_tree(
                dir_path_current=dir_path_current + dir_name, func=func,
                dir_path_rel=dir_path_rel + dir_name + "/",
                **kwargs
            )

def create_dir(dir_path):
    dir_path_obj = Path(dir_path)
    dir_path_obj.mkdir(parents=True, exist_ok=True)
    return dir_path_obj.__str__() + "/"
create_dir_if_non_exist = create_dir

def create_dir_for_file_path(file_path):
    dir_path_obj = Path(file_path).parent
    dir_path_obj.mkdir(parents=True, exist_ok=True)
    return file_path

def remove_file(file_path):
    assert file_exist(file_path)
    file_path_obj = Path(file_path)
    file_path_obj.unlink() # missing_ok=False for Python>=3.4
delete_file = remove_file

def remove_file_with_suffix(dir_path:str):
    dir_path = check_dir_exist(dir_path)
    for file_path in list_all_file_path(dir_path): 
        file_path_no_suffix, suffix = get_file_name_and_suffix
    DLUtils.file.RemoveMatchedFiles("./", r".*\.png")

def clear_dir(dir_path):
    if dir_exist(dir_path):
        try:
            remove_dir(dir_path)
            create_dir(dir_path)
        except Exception: # failed to remove dir
            for file_path in list_all_file_path(dir_path):
                remove_file(file_path)
            for dir_path in list_all_dir_path(dir_path):
                remove_dir(file_path)
    else:
        create_dir(dir_path)
    assert dir_exist(dir_path)

def _remove_dir(dir_path):
    shutil.rmtree(dir_path)

def remove_dir(dir_path): # remove a folder and all files and child folders in it
    assert dir_exist(dir_path)
    shutil.rmtree(dir_path)
    return
delete_dir = remove_dir

def remove_file_if_exist(file_path):
    if file_exist(file_path):
        remove_file(file_path)
delete_file_if_exist = remove_file_if_exist

def copy_file(file_path_source, file_path_target):
    assert file_exist(file_path_source)
    create_dir_for_file_path(file_path_target)
    shutil.copy2(file_path_source, file_path_target) # copy2() preseves timestamp. copy() does not.
    assert file_exist(file_path_target)
    return

def move_file(file_path_source, file_path_target):
    assert file_exist(file_path_source)
    assert not file_exist(file_path_target)
    create_dir_for_file_path(file_path_target)
    shutil.move(file_path_source, file_path_target)
    # Path(file_path_source).rename(file_path_target)
        # [WinError 17] 系统无法将文件移到不同的磁盘驱动器。
    assert not file_exist(file_path_source)
    assert file_exist(file_path_target)

def move_file_overwrite(file_path_source, file_path_target):
    assert file_exist(file_path_source)
    Path(file_path_source).rename(file_path_target)
    assert not file_exist(file_path_source)
    assert file_exist(file_path_target)

def get_dir_path_of_file_path(file_path):
    dir_path_obj = Path(file_path).parent
    return dir_path_obj.__str__() + "/"

def get_file_name_and_suffix(file_name):
    import re
    if file_name.endswith("/") or file_name.endswith("\\"):
        raise Exception
    match_result = re.match(r"(.*)\.(.*)", file_name)
    if match_result is None:
        return file_name, ""
    else:
        return match_result.group(1), match_result.group(2)

def get_file_path_and_suffix(file_path):
    import re
    if file_path.endswith("/") or file_path.endswith("\\"):
        raise Exception
    match_result = re.match(r"(.*)\.(.*)", file_path)
    if match_result is None:
        return file_path, ""
    else:
        return match_result.group(1), match_result.group(2)  

def get_file_path_without_suffix(file_path):
    file_path_no_suffix, suffix = get_file_name_and_suffix(file_path)
    return file_path_no_suffix

def current_script_path_without_suffix(script_file_path):
    return get_file_path_without_suffix(script_file_path)

def change_file_path_suffix(file_path:str, suffix:str):
    suffix = suffix.lstrip(".")
    file_path_no_suffix, suffix = get_file_name_and_suffix(file_path)
    assert suffix is not None
    file_path_new = file_path_no_suffix + suffix
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

import _utils_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import yaml # pip install pyyaml
else:
    yaml = _utils_import.LazyImport("yaml")

def from_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def to_yaml_file(data, file_path):
    create_dir_for_file_path(file_path)
    with open(file_path, 'w') as file:
        yaml.dump(data, file)

from _utils_import import _utils_io
import _utils_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _utils_io import (
        text_file_to_str,
        str_to_text_file,
    )
else:
    text_file_to_str = _utils_import.LazyFromImport("_utils_io", "text_file_to_str")
    str_to_text_file = _utils_import.LazyFromImport("_utils_io", "str_to_text_file")