from __future__ import annotations
import os
from pathlib import Path

def class_path_from_class_instance(Instance):
    cls = Instance.__class__
    module = cls.__module__
    qualname = cls.__qualname__
    return f"{module}.{qualname}"

def class_instance_from_class_path(ClassPath: str, *args, **kwargs):
    import importlib
    # split the class_path into module path and class name
    module_path, ClassName = ClassPath.rsplit('.', 1)
    # import the module
    module = importlib.import_module(module_path)
    # get the class
    cls = getattr(module, ClassName)
    # create an instance of the class
    instance = cls(*args, **kwargs)
    return instance

import argparse

class List(list):
    def __init__(self, list_like=None, *args):
        super().__init__()
        if list_like is not None:
            for _ in list_like:
                if isinstance(_, dict):
                    self.append(Dict(_))
                elif isinstance(_, argparse.Namespace):
                    self.append(Dict(_))
                else:
                    self.append(_)
        elif len(args) > 0:
            for arg in args:
                self.append(arg)
        else:
            pass
    
class Dict(dict):
    """
    A subclass of dict that allows attribute-style access.
    """
    def __init__(self,
            dict_like: dict = None,
            **kwargs
            # allow_missing_attr=False,
        ):
        # self.allow_missing_attr = allow_missing_attr
        """
            If allow_missing_attr == True, empty Dict object will be created and returned
                when trying to get a non-existent attribute
        """
        
        if dict_like is not None:
            assert len(kwargs) == 0
            if isinstance(dict_like, dict):
                self.from_dict(dict_like)
            elif isinstance(dict_like, argparse.Namespace):
                self.from_dict(vars(dict_like))
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
            raise AttributeError(f"'Dict' object has no attribute '{key}'")
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
            elif isinstance(value, list):
                self[key] = List(value)
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
    def update(self, dict_external:Dict=None, **kwargs):
        if len(kwargs) > 0:
            assert dict_external is None
            for key, value in kwargs.items():
                self[key] = value
            return self

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
    def update_if_not_exist(self, **kwargs):
        for key, value in kwargs.items():
            if not key in self:
                self[key] = value
        return self        
    def create_if_not_exist(self, key) -> Dict:
        if key in self:
            return self[key]
        else:
            value = Dict()
            self[key] = value
            return value
    def check_key_exist(self, key):
        assert key in self
        return self
    def set_if_not_exist(self, **_dict):
        for key, value in _dict.items():
            if key in self:
                continue
            else:
                self[key] = value
        return self
    def hasattr(self, key):
        return hasattr(self, key)
    def getattr(self, key):
        return self.get(self, key)
    def setattr(self, key=None, value=None, **kwargs):
        if len(kwargs) > 0:
            assert key is None and value is None
            for _key, _value in kwargs.items():
                self[_key] = _value
            return self
        self[key] = value
        return self
    def copy():
        return Dict(super().copy())

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