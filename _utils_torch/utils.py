from __future__ import annotations

from _utils_import import torch

def get_batch_num(torch_dataloader):
    return len(torch_dataloader)

def np_array_to_torch_tensor(np_array: torch.Tensor):
    return torch.from_numpy(np_array)

def print_torch_module(model: torch.nn.Module, pipe_out=None):
    if pipe_out is None:
        import _utils_io
        pipe_out = _utils_io.PipeOut()
    ParamDict = dict(model.named_parameters())
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