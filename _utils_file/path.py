from pathlib import Path
import os
import _utils_file

def file_path_to_unix_style(file_path: str):
    # TODO: handle ~ in file path
    file_path = file_path.replace("\\", "/")
    return file_path

def dir_path_to_unix_style(dir_path: str):
    # TODO: handle ~ in dir path
    dir_path = dir_path.replace("\\", "/")
    dir_path = dir_path.rstrip("/")
    dir_path += "/"
    return dir_path

def get_dir_path_current(__file__: str):    
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    return dir_path_current

def get_dir_path_parent(__file__: str):    
    dir_path_parent = os.path.dirname(os.path.realpath(__file__)) + "/"
    return dir_path_parent

def get_script_file_path_without_suffix(__file__):
    file_path_script = os.path.abspath(__file__)
    return _utils_file.get_file_path_without_suffix(file_path_script)

def get_script_dir_path(__file__):
    # Using os.path
    dir_path_script = os.path.dirname(os.path.abspath(__file__))
    # print(f"Using os.path: {script_dir_os}")

    dir_path_script = Path(__file__).resolve().parent.__str__()
    # print(f"Using pathlib: {script_dir_pathlib}")
    
    dir_path_script += "/"
    return dir_path_script

def get_dir_path_of_file_path(file_path: str):
    dir_path_obj = Path(file_path).parent
    return dir_path_obj.__str__() + "/"

def get_file_name_of_file_path(file_path: str):
    file_name = Path(file_path).name
    return file_name

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

def is_equiv_file_path(file_path_1, file_path_2):
    return os.path.samefile(file_path_1, file_path_2)