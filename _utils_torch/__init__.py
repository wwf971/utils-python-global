from __future__ import annotations
import numpy as np

from _utils_torch.wrapper import(
    TorchModuleWrapper,
    ModuleList, TorchModule,
    init_torch_module_from_dict,
    get_torch_module_config,
    torch_module_from_file,
    create_torch_module
)

from .mlp import (
    MLP, MLPParallel,
    build_mlp,
)

from .utils import (
    get_batch_num,
    print_torch_module,
    np_array_to_torch_tensor,
    torch_tensor_to_np_array,
    check_tensor_shape,
    to_one_hot
)

from _utils_import import torch, nn, np