
import _utils_import
from _utils_import import _utils_file
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import yaml # pip install pyyaml
else:
    yaml = _utils_import.lazy_import("yaml")

def from_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def to_yaml_file(obj, file_path, backend='local'):
    backend = backend.lower()
    if backend in ['local']:
        to_yaml_file_local(obj, file_path)
    else:
        _utils_file.create_dir_for_file_path(file_path)
        with open(file_path, 'w') as file:
            yaml.dump(obj, file, sort_keys=False)

def to_yaml_file_local(obj, file_path_save):
    _utils_file.create_dir_for_file_path(file_path_save)
    yaml_str = []
    _to_yaml_str_local(obj, indent=0, yaml_str=yaml_str, )
    yaml_str = "".join(yaml_str)
    with open(file_path_save, "w") as f:
        f.write(yaml_str)
    return

def _to_yaml_str_local(obj, indent, yaml_str:list, parent=None, parent_index=-1):
    if isinstance(obj, dict):
        index = 0
        for key, value in obj.items():
            if isinstance(parent, dict):
                yaml_str.append("".join([" " for _ in range(indent)]))
            elif isinstance(parent, list):
                if index == 0:
                    pass
                else:
                    yaml_str.append("".join([" " for _ in range(indent)]))
            else: # index != 0
                yaml_str.append("".join([" " for _ in range(indent)]))
            indent_add = len(key) + 2
            yaml_str.append(key + ": ")
            if isinstance(value, dict): # 如果dict的child也是dict, 那么就换行
                yaml_str.append("\n")
                indent_add = 2
            elif isinstance(value, list): # 如果dict的child也是dict, 那么就换行
                yaml_str.append("\n")
                if isinstance(parent, list):
                    indent_add = 0
                else:
                    indent_add = 2
            _to_yaml_str_local(
                value, indent + indent_add, yaml_str, parent=obj, parent_index=index
            )
            index += 1
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            if index == 0 and isinstance(parent, list):
                pass
            elif parent_index != 0:
                yaml_str.append("".join([" " for _ in range(indent)]))
            elif isinstance(parent, dict):
                yaml_str.append("".join([" " for _ in range(indent)]))

            yaml_str.append("- ")

            _to_yaml_str_local(
                value, indent + 2, yaml_str, parent=obj, parent_index=index
            )
    elif isinstance(obj, str):
        yaml_str.append(obj)
        yaml_str.append("\n")
    elif isinstance(obj, int):
        yaml_str.append(str(obj))
        yaml_str.append("\n")
    elif isinstance(obj, float):
        yaml_str.append(float(obj))
        yaml_str.append("\n")
    else:
        raise TypeError