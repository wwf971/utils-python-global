from pathlib import Path
import os
import _utils_file

def file_path_to_unix_style(file_path: str):
    file_path = file_path.replace("\\", "/")
    if "~" in file_path: # handle ~ in file path
        file_path = os.path.expanduser(file_path)
    return file_path

def dir_path_to_unix_style(dir_path: str, trailing_slash=True):
    if "~" in dir_path: # handle ~ in file path
        dir_path = os.path.expanduser(dir_path)
    dir_path = dir_path.replace("\\", "/")
    dir_path = dir_path.rstrip("/")
    if trailing_slash:
        dir_path += "/"
    return dir_path

def dir_path_to_win_style(dir_path: str, trailing_slash=False):
    dir_path = dir_path.lstrip("/").lstrip("\\")
    dir_path = dir_path.replace("/", "\\")
    if trailing_slash:
        dir_path += "\\"
    return dir_path

def get_dir_path_current(__file__: str):    
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    return dir_path_current

def get_dir_path_parent(__file__: str):    
    dir_path_parent = os.path.dirname(os.path.realpath(__file__)) + "/"
    return dir_path_parent

def get_file_path_current(__file__: str):
    file_path_script = os.path.abspath(__file__)
    return file_path_script

def get_file_path_current_no_suffix(__file__: str):
    file_path_script = os.path.abspath(__file__)
    return _utils_file.get_file_path_no_suffix(file_path_script)

def change_file_path_current_suffix(__file__: str, suffix=None, append_before_suffix=""):
    file_path_script = os.path.abspath(__file__)
    file_path_script_no_suffix, _suffix = _utils_file.get_file_name_and_suffix(file_path_script)
    assert _suffix is not None
    
    if suffix is None: # use current suffix
        suffix = _suffix

    return file_path_script_no_suffix + append_before_suffix + "." + suffix

def get_script_dir_path(__file__):
    # Using os.path
    dir_path_script = os.path.dirname(os.path.abspath(__file__))
    # print(f"Using os.path: {script_dir_os}")

    dir_path_script = Path(__file__).resolve().parent.__str__()
    # print(f"Using pathlib: {script_dir_pathlib}")
    
    dir_path_script += "/"
    return dir_path_script

def get_dir_name_of_dir_path(dir_path: str):
    if dir_path.endswith("/"):
        dir_path = dir_path.rstrip("/")
    if dir_path.endswith("\\"):
        dir_path = dir_path.rstrip("\\")
    dir_name = Path(dir_path).name
    return dir_name

def get_dir_path_of_file_path(file_path: str):
    dir_path_obj = Path(file_path).parent
    return dir_path_obj.__str__() + "/"

def get_file_name_of_file_path(file_path: str):
    file_name = Path(file_path).name
    return file_name

def get_dir_path_of_dir_path(dir_path: str):
    dir_path = dir_path_to_unix_style(dir_path)
    dir_path_obj = Path(dir_path).parent
    return dir_path_obj.__str__() + "/"
get_parent_dir_path = get_dir_path_of_dir_path

def get_file_name_and_suffix(file_name: str):
    import re
    if file_name.endswith("/") or file_name.endswith("\\"):
        raise Exception
    match_result = re.match(r"(.*)\.(.*)", file_name)
    if match_result is None:
        return file_name, ""
    else:
        return match_result.group(1), match_result.group(2)

def get_file_path_and_suffix(file_path: str):
    import re
    if file_path.endswith("/") or file_path.endswith("\\"):
        raise Exception
    match_result = re.match(r"(.*)\.(.*)", file_path)
    if match_result is None:
        return file_path, ""
    else:
        return match_result.group(1), match_result.group(2)

def get_file_name_suffix(file_path: str):
    _, suffix = get_file_name_and_suffix(file_path)
    return suffix

def get_file_path_suffix(file_path: str):
    _, suffix = get_file_path_and_suffix(file_path)
    return suffix
get_file_suffix = get_file_path_suffix

def is_equiv_file_path(path_1, path_2):
    norm_path1 = os.path.normpath(os.path.abspath(path_1))
    norm_path2 = os.path.normpath(os.path.abspath(path_2))
    return norm_path1 == norm_path2

    # return os.path.samefile(file_path_1, file_path_2)
        # both file and dir path ok
        # raise error if path_1 or path_2 don't exist