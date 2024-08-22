# all dir_path returned end with / or \\.
import os
from pathlib import Path
from _utils_import import pickle

def file_exist(file_path):
    return Path(file_path).is_file()

def check_file_exist(file_path):
    assert file_exist(file_path)
    return file_path

def dir_exist(dir_path):
    return Path(dir_path).is_dir()

def check_dir_exist(dir_path):
    assert dir_exist(dir_path)
    return dir_path

def list_all_file_name(dir_path):
    file_name_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    return file_name_list

def list_all_dir_name(dir_path):
    dir_name_list = [f + "/" for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
    return dir_name_list

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
    for FileName in list_all_file_name(dir_path_current):
        func(dir_path_current=dir_path_current, FileName=FileName, dir_path_rel=dir_path_rel, **kwargs)
    if recur:
        for dir_name in list_all_dir_name(dir_path_current):
            visit_tree(
                dir_path_current=dir_path_current + dir_name, func=func,
                dir_path_rel=dir_path_rel + dir_name + "/",
                **kwargs
            )

def create_dir_if_non_exist(dir_path):
    dir_path_obj = Path(dir_path)
    dir_path_obj.mkdir(parents=True, exist_ok=True)
    return dir_path_obj.__str__() + "/"

def create_dir_for_file_path(file_path):
    dir_path_obj = Path(file_path).parent
    dir_path_obj.mkdir(parents=True, exist_ok=True)
    return file_path

def remove_file(file_path):
    assert file_exist(file_path)
    file_path_obj = Path(file_path)
    file_path_obj.unlink() # missing_ok=False for Python>=3.4

def get_dir_path_of_file_path(file_path):
    dir_path_obj = Path(file_path).parent
    return dir_path_obj.__str__() + "/"

def get_file_name_and_suffix(file_name):
    import re
    if file_name.endswith("/") or file_name.endswith("\\"):
        raise Exception()
    match_result = re.match(r"(.*)\.(.*)", file_name)
    if match_result is None:
        return file_name, ""
    else:
        return match_result.group(1), match_result.group(2)

def get_file_path_without_suffix(file_path):
    file_path_no_suffix, suffix = get_file_name_and_suffix(file_path)
    return file_path_no_suffix

def current_script_path_without_suffix(script_file_path):
    return get_file_path_without_suffix(script_file_path)


def to_file(obj, file_path):
    file_path = create_dir_for_file_path(file_path)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)

def from_file(file_path):
    file_path = check_file_exist(file_path)    
    with open(file_path, 'rb') as f:
        obj = pickle.load(f, encoding='bytes')
    return obj