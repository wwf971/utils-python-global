from _utils_import import Dict
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