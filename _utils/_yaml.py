
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

def to_yaml_file(data, file_path):
    _utils_file.create_dir_for_file_path(file_path)
    with open(file_path, 'w') as file:
        yaml.dump(data, file)