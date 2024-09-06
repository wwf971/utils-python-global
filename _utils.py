from __future__ import annotations
import os
from pathlib import Path
def GetScriptDirPath(__File__=None, EndWithSlash=True):
    if __File__ is None:
        __File__ = __file__
    # Using os.path
    script_dir_os = os.path.dirname(os.path.abspath(__File__))
    print(f"Using os.path: {script_dir_os}")

    # Using pathlib
    script_dir_pathlib = Path(__File__).resolve().parent.__str__()
    print(f"Using pathlib: {script_dir_pathlib}")
    
    if EndWithSlash:
        script_dir_pathlib += "/"
    return script_dir_pathlib
GetCurrentScriptDirPath = GetScriptDirPath

def class_path_from_class_instance(Instance):
    cls = Instance.__class__
    module = cls.__module__
    qualname = cls.__qualname__
    return f"{module}.{qualname}"

def class_instance_from_class_path(ClassPath: str, **KwArgs):
    import importlib
    # split the class_path into module path and class name
    ModulePath, ClassName = ClassPath.rsplit('.', 1)
    # import the module
    module = importlib.import_module(ModulePath)
    # get the class
    cls = getattr(module, ClassName)
    # create an instance of the class
    instance = cls(**KwArgs)
    return instance

class List(list):
    def __init__(self, *args):
        super().__init__()
        for arg in args:
            self.append(arg)
    

class Dict(dict):
    """
    A subclass of dict that allows attribute-style access.
    """
    def __init__(self,
            source: dict = None,
            **kwargs
            # allow_missing_attr=False,
        ):
        # self.allow_missing_attr = allow_missing_attr
        """
            If allow_missing_attr == True, empty Dict object will be created and returned
                when trying to get a non-existent attribute
        """
        if source is not None:
            assert len(kwargs) == 0
            if isinstance(source, dict):
                self.from_dict(source)
            elif isinstance(source, argparse.Namespace):
                self.from_dict(vars(source))
            else:
                raise TypeError
        elif len(kwargs) > 0:
            self.from_dict(kwargs)
        else:
            self.from_dict({})
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'AttrDict' object has no attribute '{key}'")
    def __setattr__(self, key, value):
        """
        will be called when setting attribtue in this way: DictObj.a = b
        """
        self[key] = value
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'AttrDict' object has no attribute '{key}'")
    def hasattr(self, key):
        return key in self

    def from_dict(self, _dict: dict):
        if not isinstance(_dict, dict):
            raise TypeError("Expect a dictionary")
        for key, value in _dict.items():
            if isinstance(value, dict):
                self[key] = Dict(value)
            else:
                self[key] = value
        return self
    def to_dict(self):        
        _dict = dict()
        for key, value in self.items():
            if isinstance(value, Dict):
                _dict[key] = value.to_dict()
            else:
                _dict[key] = value
        return _dict
    def update(self, dict_external:Dict):
        for key, value in dict_external.items():
            if isinstance(value, dict) and not isinstance(value, Dict):
                value = Dict(value)
            if not hasattr(self, key):
                self[key] = value
                continue

            value_old = self[key]
            if isinstance(value_old, dict):
                if not isinstance(value_old, Dict):
                    value_old = Dict(value_old)
                value_old.update(value)
            else:
                self[key] = value # overwrite
        return self
    def create_if_non_exist(self, key) -> Dict:
        if key in self:
            return self[key]
        else:
            value = Dict()
            self[key] = value
            return value
    def check_key_exist(self, key):
        assert key in self
        return self
    def set_if_non_exist(self, **_dict):
        for key, value in _dict.items():
            if key in self:
                continue
            else:
                self[key] = value
        return self
    def hasattr(self, key):
        return hasattr(self, key)

class DefaultDict(Dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # if self.allow_missing_attr:
            child = Dict()
            setattr(self, key, child)
            return child
            # else:
            #     raise AttributeError(f"'AttrDict' object has no attribute '{key}'")

# class Obj(List, Dict):
class Obj():
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            assert len(kwargs) == 0
            self.core = List(*args)
        elif len(kwargs) > 0:
            self.core = Dict(**kwargs)
        else:
            self.core = Dict()
    def __getattr__(self, key):
        return self.core.__getattr__(key)
    def __setattr__(self, key, value):
        if key == "core":
            super().__setattr__(key, value) # bypass custom __setattr__
        else:
            setattr(self.core, key, value)
    def __len__(self):
        return len(self.core)
    def __getitem__(self, index):
        return self.core[index]

if __name__ == "__main__":
    obj =List(
        Dict(A=1, B=2),
        Dict(C=3, D=4)
    )
    print(obj[0].A)
    obj = Obj(
        Obj(A=1, B=2),
        Obj(C=3, D=4)
    )
    print(obj[1].D)
    a = 1

    # Example usage:
    d = Dict()
    d.a = 10
    print(d.a)  # Output: 10
    print(d['a'])  # Output: 10

    d['b'] = 20
    print(d.b)  # Output: 20

    del d.a
    # print(d.a)  # Raises AttributeError