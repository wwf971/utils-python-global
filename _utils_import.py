"""
check import time:
    python -X importtime _lib_import.py
"""

import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grandparent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current,
    dir_path_current + "/utils-python-global",
]
try:
    from _utils_import_path import sys_path_list
except Exception:
    pass
else:
    for sys_path in sys_path_list:
        sys.path.append(sys_path)
LAZY_IMPORT = True

import importlib
def import_module(module_path: str):
    module_path = importlib.import_module(module_path)
    return module_path

def import_module_from_module_path_list(module_path_list: list):
    # import a.b.c --> import_module_from_module_path_list(["a", "b", "c"])
    assert len(module_path_list) > 1
    submodule = importlib.import_module(".".join(module_path_list))
    return submodule

def lazy_import(module_path, after_import=None, print_stack_on_first_import=False):
    """
    import a => LazyImport("a") # lazy import module
    import a.b => LazyImport("a.b") # lazy import submodule
    module, submodule
    """
    return LazyImport(module_path, import_mode="module", after_import=after_import, print_stack_on_first_import=print_stack_on_first_import)

def from_import(module_path: str, var_str: str):
    """
    from a.b import c as d => d = FromImport("a.b", "c")
    """
    module = import_module(module_path)
    var = getattr(module, var_str)
    return var

def lazy_from_import(ModuleStr: str, VarStr: str):
    """
    from a.b import c as d => d = lazy_from_import("a.b", "c")
    """
    return LazyImport(ModuleStr, VarStr, import_mode="from_import")

class LazyImport(object):
    def __init__(self,
        module_name: str,
        var_name: str = None, 
        raise_on_import_error: bool=True,
        import_mode="import", # "import", "from_import"
        after_import=None,
        print_stack_on_first_import=False
    ):
        self.module_name = module_name
        self.var_name = var_name
        self.raise_on_import_error = raise_on_import_error
        self.is_module_imported = False
        self.import_mode = import_mode
        self.after_import = after_import
        self.print_stack_on_first_import = print_stack_on_first_import
        self.init()
    def init(self):
        self.module_path_list = self.module_name.split(".")
        if len(self.module_path_list) == 1:
            self.import_module = self._import_module
        elif len(self.module_path_list) > 1:
            self.import_module = self._import_submodule
        else:
            raise Exception
        if self.import_mode in ["module", "submodule", "import"]:
            self.import_mode = "import"
            self._import = self._import_module
            self.is_from_import = False
        elif self.import_mode in ["from_module_import", "from_submodule_import", "from", "from_import"]:
            self.import_mode = "from_import"
            self._import = self._from_import
            self.is_from_import = True
        else:
            raise ValueError(self.import_mode)
    def _import_module(self):
        # assert not self.is_module_imported
        import importlib
        try:
            module = importlib.import_module(self.module_name)
        except Exception:
            if self.raise_on_import_error:
                raise Exception(f"Failed to import module: %s"%{self.module_name})
            else:
                self.is_module_imported = False
                module = "_utils_import.LazyImport: ImportFailure"
                return None
        else:
            self.is_module_imported = True
        self.module = module
        if self.after_import is not None:
            self.after_import(module)
        if self.print_stack_on_first_import:
            import traceback
            traceback.print_stack()
        return module
    def _import_submodule(self):
        module = import_module_from_module_path_list(self.module_path_list)
        self.module = module
        if self.after_import is not None:
            self.after_import(module)
        if self.print_stack_on_first_import:
            import traceback
            traceback.print_stack()
        return module
    def _from_import(self):
        module = self.import_module()
        var = getattr(module, self.var_name)
        self.var = var
        return var
    def __call__(self, *List, **Dict):
        if not self.is_module_imported:
            self._import()    
        return self.var(*List, **Dict)
    def __getattr__(self, Name):
        if not self.is_module_imported:
            self._import()
        if self.is_from_import:
            return getattr(self.var, Name)
        else:
            var = getattr(self.module, Name) # submodule, method, variable etc
            setattr(self, Name, var)
            return var
    def __getstate__(self): # called when serialize this object
        # Create a copy of the instance's dictionary
        state = {}
        # Remove the module and other non-serializable attributes
        # Store the import status separately to avoid re-importing during unpickling
        state['is_module_imported'] = False
        state['import_mode'] = self.import_mode
        state['module_name'] = self.module_name
        state['var_name'] = self.var_name
        state['after_import'] = self.after_import
        state['print_stack_on_first_import'] = self.print_stack_on_first_import
        return state
    def __setstate__(self, state): # called when deserialize this object
        self.__dict__.update(state)
        self.init()

import pickle # lazy_import pickle can be buggy
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy as np
    import pandas as pd
    import scipy
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import matplotlib as mpl
    from matplotlib import pyplot as plt
    from PIL import Image as Im
    import cv2
    import psutil
    import shutil
    import _utils
    import _utils_io
    import _utils_file
    import _utils_system
    import _utils_image
    from _utils import Dict, List
    import datetime
else:
    np = lazy_import("numpy")
    pd = lazy_import("pandas")
    scipy = lazy_import("scipy")
    torch = lazy_import("torch")
    nn = lazy_from_import("torch", "nn")
    F = lazy_import("torch.nn.functional")
    mpl = lazy_import("matplotlib")
    plt = lazy_import("matplotlib.pyplot")
    Im = lazy_import("PIL.Image")
    cv2 = lazy_import("cv2")
    psutil = lazy_import("psutil")
    shutil = lazy_import("shutil")
    _utils = lazy_import("_utils")
    _utils_io = lazy_import("_utils_io")
    _utils_file = lazy_import("_utils_file")
    _utils_system = lazy_import("_utils_system")
    _utils_image = lazy_import("_utils_image")
    Dict = lazy_from_import("_utils", "Dict")
    List = lazy_from_import("_utils", "List")
    datetime = lazy_import("datetime")

# """import DLUtils module"""
import time
# if TYPE_CHECKING:
#     import DLUtils
# else:
#     if LAZY_IMPORT:
#         # lazy import
#         print("Import DLUtils(Lazy).", end=" ")
#         TimeStart = time.time()
#         DLUtils = LazyImport("DLUtils", print_stack_on_first_import=False)
#         TimeEnd = time.time()
#         TimeImport = TimeEnd - TimeStart
#         print("Finished. Time: %.3fs"%(TimeImport))
#     else:
#         # direct import
#         print("Import DLUtils.", end=" ")
#         TimeStart = time.time()
#         import DLUtils
#         TimeEnd = time.time()
#         TimeImport = TimeEnd - TimeStart
#         print("Finished. Time: %.3fs"%(TimeImport))