
import _utils_import
from _utils_import import _utils_file
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import yaml # pip install pyyaml
    import ruamel.yaml as ruamel_yaml
else:
    yaml = _utils_import.lazy_import("yaml")
    ruamel_yaml = _utils_import.lazy_import("ruamel.yaml")

class YAMLDict:
    def __init__(self, file_path=None):
        self.yaml_obj = ruamel_yaml.YAML()
        self.yaml_dict = {}  # Use a private attribute to avoid recursion
        if file_path is not None:
            self.from_file(file_path)

    def from_file(self, file_path):
        self.yaml_dict = self.yaml_obj.load(_utils_file.text_file_to_str(file_path))
        return self.yaml_dict

    def get_dict(self):
        return self.yaml_dict

    def to_file(self, file_path):
        with open(file_path, 'w') as f:
            self.yaml_obj.dump(self.get_dict(), f)  # keep comment

    def __getattr__(self, name): # only triggered when accessing non-existent attribute
        # but not applicable for magic methods
        return getattr(self.__dict__['yaml_dict'], name)

    def __getitem__(self, key):
        return self.yaml_dict[key]

    def __setitem__(self, key, value):
        self.yaml_dict[key] = value

    def __setattr__(self, key, value):
        if key in ['yaml_dict', 'yaml_obj']:
            super().__setattr__(key, value)
        else:
            self.__dict__['yaml_dict'][key] = value

    def __delattr__(self, key):
        if key in self.yaml_dict:
            del self.yaml_dict[key]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
    def __contains__(self, key):
        return key in self.yaml_dict
    
    
def from_yaml_file(file_path, backend='default'):
    if backend in ['ruamel']:
        yaml_obj = ruamel_yaml.YAML()
        yaml_dict = yaml_obj.load(_utils_file.text_file_to_str(file_path)) # keep comment
        return yaml_dict
    else:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
    return data

def obj_to_yaml_file(obj, file_path, backend:str='local'):
    backend = backend.lower()
    if backend in ['local']:
        to_yaml_file_local(obj, file_path)
    else:
        _utils_file.create_dir_for_file_path(file_path)
        with open(file_path, 'w') as file:
            yaml.dump(obj, file, sort_keys=False)
to_yaml_file = obj_to_yaml_file

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
    # elif isinstance(obj, np.ndarray):
        # pass
    elif isinstance(obj, str):
        yaml_str.append(obj)
        yaml_str.append("\n")
    elif isinstance(obj, int):
        yaml_str.append(str(obj))
        yaml_str.append("\n")
    elif isinstance(obj, float):
        yaml_str.append(str(obj))
        yaml_str.append("\n")
    else:
        obj_str = str(obj)
        if not "\n" in obj_str:
            yaml_str.append(obj_str)
        else:
            yaml_str.append(str(type(obj)))
        yaml_str.append("\n")