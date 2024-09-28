from pathlib import Path
import os
def get_dir_path_of_file_path(file_path: str):
    dir_path_obj = Path(file_path).parent
    return dir_path_obj.__str__() + "/"

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