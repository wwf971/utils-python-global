from __future__ import annotations
from _utils_import import torch, nn, np, _utils_image, Dict
from _utils_torch.wrapper import(
    TorchModuleWrapper,
    ModuleList, TorchModule,
    init_torch_module_from_dict,
    get_torch_module_config,
    torch_module_from_file,
    create_torch_module,
    get_torch_module_param_num
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

def torch_tensor_to_image_file(tensor, file_path_save, shape="chw", value_range=[0.0, 1.0]):
    assert len(list(tensor.size())) == 3
    array = torch_tensor_to_np_array(tensor)
    shape = shape.lower()
    if shape in ["chw"]:
        array = array.transpose(1, 2, 0)
    array = (array - value_range[0]) / (value_range[1] - value_range[0])
        # --> value_range: [0.0, 1.0]
    array = array.clip(0.0, 1.0)
    _utils_image.image_np_float01_to_file(array, file_path_save)

def get_device_with_largest_available_useage():
    import _utils_gpu
    return "cuda:%d"%_utils_gpu.get_gpu_with_largest_available_useage()