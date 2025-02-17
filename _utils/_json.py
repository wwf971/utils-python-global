from _utils_import import Dict, _utils_file
import json
def json_str_to_dict(str_json):
    # from types import SimpleNamespace
    json_dict = json.loads(str_json, object_hook=lambda d: Dict(**d)) #  Dict可以用SimpleNamespace替代
    return json_dict

def json_str_to_dict_test():
    str_json = '{"name": "John Smith", "hometown": {"name": "New York", "id": 123}}'
    json_dict = json_str_to_dict(str_json)
    print(json_dict.name, json_dict.hometown.name, json_dict.hometown.id)
    return

def obj_to_json_file(_dict, file_path_save):
    _utils_file.create_dir_for_file_path(file_path_save)
    with open(file_path_save, "w") as json_file:
        json.dump(_dict, json_file, indent=4)  # indent using space
    return
dict_to_json_file = obj_to_json_file