from _utils_import import np, torch, nn, F
import _utils_torch
from _utils import (
    Dict,
    class_path_from_class_instance,
    class_instance_from_class_path,
)

from .utils import (
    np_array_to_torch_tensor
)
import _utils_file

# a lightweight wrapper of torch.nn.Module
class TorchModuleWrapper(nn.Module):
    """
    
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.config = Dict()
        if len(args) + len(kwargs) > 0:
            self.init(*args, **kwargs)
    def init(self, **kwargs):
        self.__has_init = True
        self.config.update(kwargs)
        return self
    def has_init(self):
        return hasattr(self, "__has_init") and self.__has_init
    def build(self):
        for name, child in dict(self.named_children()).items():
            if isinstance(child, TorchModuleWrapper):
                child.build()
            elif isinstance(child, torch.nn.Module):
                build_torch_module(child)
            else:
                raise TypeError
        return self
    def get_class_path(self):
        return class_path_from_class_instance(self)
    def add_param(self, name=None, param=None, **param_dict):
        if len(param_dict) > 0:
            assert name is None and param is None
            self.add_params(**param_dict)
            return self
    
        if isinstance(param, np.ndarray):
            param = torch.from_numpy(param).float() # dtype=float32
        self.register_parameter(
            name, torch.nn.Parameter(param)
        )
        return self
    def add_params(self, **ParamDict):
        """add many pairs of params to torch module"""
        for name, Param in ParamDict.items():
            self.add_param(name, Param)
    def add_buffer(self, name, Value: torch.Tensor, **BufferDict):
        self.register_buffer(name, Value)
        if len(BufferDict) > 0:
            self.add_buffers(**BufferDict)
        return self
    def add_buffers(self, **BufferDict):
        for name, Param in BufferDict.items():
            self.add_buffer(name, Param)
        return self
    def add_submodule(self, name=None, submodule=None, **submodule_dict):
        if len(submodule_dict) > 0:
            assert name is None and submodule is None
            for submodule_name, SubModule in submodule_dict.items():
                self.add_submodule(submodule_name, SubModule)
            return
        if isinstance(submodule, TorchModuleWrapper):
            self.add_module(name, submodule)
        else:
            assert isinstance(submodule, torch.nn.Module)
            self.add_module(name, submodule)
        # setattr(self, name, Module)
            # torch will check if Module is subclass of torch.nn.Module
        return self
    def add_submodules(self, **module_dict):
        for name, child in module_dict.items():
            self.add_submodule(name, child)
        return self
    def get_submodule(self, submodule_name):
        assert submodule_name in self.get_child_name_list()
        return getattr(self, submodule_name)
    def add_torch_module(self, name, torch_module_class, **kwargs):
        torch_module = torch_module_class(**kwargs)
        torch_module.config = {
            "init_args": kwargs
        }
        self.add_module(name, torch_module)
        return self
    def AddModuleList(self, name, *module_list, **module_dict):
        if len(module_list) > 0:
            # Modulename will be like "1", "2", ...
            assert len(module_list) == 0
            self.add_submodule(
                name,
                ModuleList().init(
                    *module_list
                )
            )
        elif len(module_dict) > 0:
            assert len(module_list) == 0
            self.add_submodule(
                name,
                ModuleList().init(
                    **module_dict
                )
            )
        else:
            raise Exception()
        return self
    def get_param_dict(self):
        ParamDict = get_torch_module_param_dict(self)
        return ParamDict
    def load_param_dict(self, ParamDict):
        load_torch_module_param_dict(self, ParamDict)
    def get_buffer_dict(self):
        buffer_dict = get_torch_module_buffer_dict(self)
        return buffer_dict
    def load_buffer_dict(self, BufferDict):
        load_torch_module_buffer_dict(self, BufferDict)
    def get_child_name_list(self):
        ChildnameList = []
        for name, SubModule in dict(self.named_children()).items():
            if "." in name:
                continue
            else:
                ChildnameList.append(name)
        return ChildnameList
    def get_submodule_dict(self):
        # get a dict of submodules
        submodule_dict = {}
        for name, child in dict(self.named_children()).items():
            if "." in name:
                continue
            if isinstance(child, TorchModuleWrapper):
                submodule_dict[name] = child.get_module_dict()
            else:
                assert isinstance(child, torch.nn.Module)
                submodule_dict[name] = get_torch_module_dict(child)
        return submodule_dict
    def load_submodule_dict(self, submodule_dict: dict):
        # load submodules
        submodule_dict = Dict(submodule_dict)
        for name, child_dict in submodule_dict.items():
            child_dict = Dict(child_dict)
            child_class_path = child_dict._class_path
            if "init_args" in child_dict.config:
                init_args = child_dict.config["init_args"]
            else:
                init_args = {}
            child = class_instance_from_class_path(
                child_class_path,
                **init_args
            )
            # recur
            if isinstance(child, TorchModuleWrapper):
                child.load_submodule_dict(child_dict.submodules)
            else:
                assert isinstance(child, torch.nn.Module)
                init_torch_module_from_dict(child, child_dict)
            self.add_submodule(name, child)
        return self
    def get_module_dict(self):
        self.config._class_path = self.get_class_path() # for debug
        return {
            "config": self.config.to_dict(),    
            "param": self.get_param_dict(),
            "buffer": self.get_buffer_dict(),
            "submodules": self.get_submodule_dict(), # submodules
            "_class_path": self.get_class_path()
        }
    def from_dict(self, module_dict: dict, load_submodule_dict=True):
        module_dict = Dict(module_dict)
        self.config = Dict(module_dict.config)
        self.load_param_dict(module_dict.param)
        self.load_buffer_dict(module_dict.buffer)
        if load_submodule_dict:
            self.load_submodule_dict(module_dict.submodules)
        return self
    def to_file(self, file_path):
        file_path = _utils_file.create_dir_for_file_path(file_path)
        self_module_dict = self.get_module_dict()
        import DLUtils
        DLUtils.file.ObjToBinaryFile(self_module_dict, file_path)
        return self
    def from_file(self, file_path):
        assert not self.has_init()
        self.clear()
        file_path = _utils_file.create_dir_for_file_path(file_path)
        module_dict = _utils_file.from_file(file_path)
        self.from_dict(module_dict, load_submodule_dict=True)
        return self
    def clear(self):
        if hasattr(self, "config"):
            delattr(self, "config")
        if hasattr(self, "_HasBuild"):
            delattr(self, "_HasBuild")
        if hasattr(self, "_IsLoad"):
            delattr(self, "_IsLoad")
        return self
    # def __repr__(self):
    #     return PrintTorchModule(self)
TorchModule = TorchModuleWrapper

def print_module_param(model: torch.nn.Module, stdout=None):
    # print(model)
    if stdout is None:
        import _utils_io
        stdout = _utils_io.PipeOut()
    ParamDict = dict(model.named_parameters())
    TrainParamList = []
    for name, value in ParamDict.items():
        TrainParamList.append(name)
        stdout.print("param: %s.\t%s."%(name, value.shape))
    return TrainParamList



def print_torch_module_submodule(model: torch.nn.Module, pipe_out=None):
    if pipe_out is None:
        import _utils_io
        pipe_out = _utils_io.PipeOut()
    submodule_dict = dict(model.named_children()) # list direct submodule of the module
    for name, child in submodule_dict.items():
        pipe_out.print("%s %s"%(name, child))    
    return

def get_torch_module_param_num(Module: torch.nn.Module):
    param_num = sum(p.numel() for p in Module.parameters())
    # print(f"Total number of parameters: {total_params}")
    return param_num

def get_torch_module_config(module: torch.nn.Module):
    if hasattr(module, "config"):
        config = module.config
        if isinstance(config, Dict):
            return config.to_dict()
        else:
            return config
    else:
        config = Dict()
        # if isinstance(Module, torch.nn.Linear):
        #     config.init_args.in_features = Module.in_features
        #     config.init_args.out_features = Module.out_features
        #     config.init_args.bias = Module

        # if len(config) == 0:
        #     return None
        # else:
        #     return config
        return config.to_dict()

def load_torch_module_param_dict(Module: torch.nn.Module, ParamDict):
    for name, np_array in ParamDict.items():
        assert isinstance(np_array, np.ndarray)
        tensor = np_array_to_torch_tensor(np_array)
        Module.register_parameter(name, nn.Parameter(tensor))

def load_torch_module_buffer_dict(Module: torch.nn.Module, BufferDict):
    for name, np_array in BufferDict.items():
        assert isinstance(np_array, np.ndarray)
        Tensor = np_array_to_torch_tensor(np_array)
        Module.register_buffer(name, Tensor)

def get_torch_module_buffer_dict(Module: torch.nn.Module):
    buffer_dict = {}
    for name, tensor in dict(Module.named_buffers()).items():
        assert isinstance(tensor, torch.Tensor)
        if "." in name:
            continue
        buffer_dict[name] = tensor.cpu().detach().numpy()
    return buffer_dict

def get_torch_module_param_dict(Module: torch.nn.Module):
    param_dict = {}
    for name, tensor in dict(Module.named_parameters()).items():
        if "." in name:
            continue
        param_dict[name] = _utils_torch.torch_tensor_to_np_array(tensor)
    return param_dict

def get_torch_module_submodule_dict(module: torch.nn.Module):
    submodule_dict = {}
    for name, child in dict(module.named_children()).items():
        if "." in module: # not direct submodule
            continue
        submodule_dict[module] = get_torch_module_dict(module)
    return submodule_dict

def get_torch_module_dict(Module: torch.nn.Module):
    module_dict = {
        "config": get_torch_module_config(Module),
        "param": get_torch_module_param_dict(Module),
        "buffer": get_torch_module_buffer_dict(Module),
        "submodules": get_torch_module_submodule_dict(Module),
        "_class_path": class_path_from_class_instance(Module)
    }
    return module_dict

def build_torch_module(module: torch.nn.Module, OutPipe=None):
    for name, submodule in dict(module.named_children()).items():
        if "." in name:
            continue
        if isinstance(module, TorchModuleWrapper):
            module.build()
        elif isinstance(module, torch.nn.Module):
            build_torch_module(submodule)
        else:
            raise TypeError

def torch_module_to_file(Module: torch.nn.Module, FilePath, OutPipe=None):
    _utils_file.to_file(get_torch_module_dict(Module), FilePath)
    return

def torch_module_from_file(file_path):
    file_path = _utils_file.create_dir_for_file_path(file_path)
    module_dict = _utils_file.from_file(file_path)
    return create_torch_module_from_dict(module_dict)

def create_torch_module(module_class, **kwargs):
    module = module_class(**kwargs)
    module.config = {
        "init_args": kwargs
    }
    return module

def create_torch_module_from_dict(module_dict: dict):
    assert isinstance(module_dict, dict)
    module_dict = Dict(module_dict)
    class_path = module_dict._class_path

    module = class_instance_from_class_path(class_path)
    if isinstance(module, TorchModuleWrapper):
        module.from_dict(module_dict)
    elif isinstance(module, torch.nn.Module):
        init_torch_module_from_dict(module, module_dict) # init after create
    else:
        raise Exception()
    return module

def init_torch_module_from_dict(module: torch.nn.Module, module_dict: dict, load_submodule_dict=True):
    module_dict = Dict(module_dict)
    module.config = Dict(module_dict.config)
    load_torch_module_param_dict(module, module_dict.param)
    load_torch_module_buffer_dict(module, module_dict.buffer)
    if load_submodule_dict:
        create_torch_module_submodule_from_dict(module, module_dict.submodules)
    return module

def create_torch_module_submodule_from_dict(parent_module: torch.nn.Module, submodule_dict):
    # load submodules
    for name, child_dict in submodule_dict.items():
        child_class_path = submodule_dict._class_path
        if "init_args" in submodule_dict.config:
            init_args = submodule_dict.config["init_args"]
        else:
            init_args = {}
        child = class_instance_from_class_path(child_class_path, **init_args)
        create_torch_module_from_dict(child_dict) # recur
        parent_module.add_module(name, child)
    return parent_module


class ModuleList(TorchModuleWrapper):
    def init(self, *module_list, **module_dict):
        if len(module_list) > 0:
            assert len(module_dict) == 0
            for Index, Module in enumerate(module_list):
                self.add_submodule(
                    "%d"%Index, Module
                )
        elif len(module_dict) > 0:
            assert len(module_list) == 0
            for name, Module in module_dict.items():
                self.add_submodule(
                    name, Module
                )
        return self
    def build(self):
        self.module_list = []
        for name, child in self.named_children():
            self.module_list.append(child)
        return super().build()
    def forward(self, x):
        y = x
        for submodule in self.module_list:
            y = submodule(y)
        return y