from __future__ import annotations

from _utils_import import np, torch, nn, F

def get_activation_func_class(func_str: str):
    func_str = func_str.lower()
    if func_str in ["relu"]:
        return nn.ReLU
    elif func_str in ["tanh"]:
        return nn.Tanh
    elif func_str in ["sigmoid"]:
        return nn.Sigmoid
    elif func_str in ["none", "identity"]:
        return nn.Identity
    elif func_str in ["relu_tanh"]:
        return lambda :nn.Sequential(nn.ReLU(), nn.Tanh()) # range: (0, 1)
    else:
        raise ValueError

def get_batch_num(torch_dataloader):
    return len(torch_dataloader)

def np_array_to_torch_tensor(np_array: torch.Tensor):
    return torch.from_numpy(np_array)

def torch_tensor_to_np_array(tensor: np.ndarray) -> np.ndarray:
    return tensor.cpu().detach().numpy()

def torch_tensor_to_np_array_nested(obj, in_place=False):
    """
    Convert torch tensors to numpy arrays in a nested object (dict/list).
    
    Args:
        obj: The object to process (can be nested dict/list)
        in_place: If True, modify the original object in place. If False, create a copy.
    
    Returns:
        The processed object with torch tensors converted to numpy arrays
    """
    if in_place:
        return _convert_tensors_in_place(obj)
    else:
        return _convert_tensors_copy(obj)

def _convert_tensors_in_place(obj):
    """Convert torch tensors to numpy arrays in place."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, torch.Tensor):
                obj[key] = torch_tensor_to_np_array(value)
            elif isinstance(value, (dict, list)):
                _convert_tensors_in_place(value)
        return obj
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            if isinstance(value, torch.Tensor):
                obj[i] = torch_tensor_to_np_array(value)
            elif isinstance(value, (dict, list)):
                _convert_tensors_in_place(value)
        return obj
    else:
        # For non-dict/list objects, return as is (no deep copy needed)
        return obj


def _convert_tensors_copy(obj):
    """Create a copy of the object with torch tensors converted to numpy arrays."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if isinstance(value, torch.Tensor):
                result[key] = torch_tensor_to_np_array(value)
            elif isinstance(value, (dict, list)):
                result[key] = _convert_tensors_copy(value)
            else:
                # For other objects, use the same reference (no deep copy)
                result[key] = value
        return result
    elif isinstance(obj, list):
        result = []
        for value in obj:
            if isinstance(value, torch.Tensor):
                result.append(torch_tensor_to_np_array(value))
            elif isinstance(value, (dict, list)):
                result.append(_convert_tensors_copy(value))
            else:
                # For other objects, use the same reference (no deep copy)
                result.append(value)
        return result
    else:
        # For non-dict/list objects, return as is (no deep copy needed)
        return obj

def check_tensor_shape(tensor, *shape):
    assert len(tensor.size()) == len(shape)
    for dimension_index, dimension_size in enumerate(shape):
        assert tensor.size(dimension_index) == dimension_size

def to_one_hot(class_index, class_num):
    # assert len(Data.shape) == 1
    return F.one_hot(class_index.long(), num_classes=class_num)

def print_torch_module(model: torch.nn.Module, pipe_out=None):
    if pipe_out is None:
        import _utils_io
        pipe_out = _utils_io.PipeOut()
    ParamDict = dict(model.named_parameters())

    from _utils import class_path_from_class_instance
    pipe_out.print("model: %s"%(class_path_from_class_instance(model)))
    with pipe_out.increased_indent():
        for name, Param in ParamDict.items():
            if "." in name: # Param belongs to one of child modules.
                continue
            pipe_out.print("param: %s.\t%s."%(name, list(Param.shape)))
        SubModuleDict = dict(model.named_children()) # list direct submodule of the module
        for name, SubModule in SubModuleDict.items():
            pipe_out.print("SubModule: %s. class: %s"%(
                name,
                SubModule._get_name() # torch.nn.Linear ==> name
            ))
            with pipe_out.increased_indent():
                print_torch_module(SubModule, pipe_out=pipe_out)


def copy_param(module_src, module_dst):
    for param_src, param_dst in zip(module_src.parameters(), module_dst.parameters()):
        param_dst.data.copy_(param_src.data)