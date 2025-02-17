from __future__ import annotations
from _utils_import import _utils_file, _utils_image
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
    to_one_hot,
    get_activation_func_class
)

def get_random_tensor_uniform(shape, start, end, device=None):
    tensor = torch.FloatTensor(*shape).uniform_(start, end)
    if device is not None:
        tensor = tensor.to(device)
    return tensor

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
    if torch.cuda.is_available():
        import _utils_gpu
        return "cuda:%d"%_utils_gpu.get_gpu_with_largest_available_useage()
    else:
        return "cpu"

def save_images_as_grid(img: torch.Tensor, file_path_save):
    from torchvision import transforms
    _utils_file.create_dir_for_file_path(file_path_save)
    # concat 4x4 images
    if len(img.shape) == 4:
        N, C, H, W = img.shape
    else:
        N, H, W = img.shape
        C = 1
        img = img.unsqueeze(0) # (1, N, H, W)
    
    row_num, col_num = _utils_image.get_row_num_and_col_num(N)
    img = torch.permute(img, (1, 0, 2, 3)) # (C, N, H, W)
    img = torch.reshape(img, (C, col_num, row_num * H, W))
    img = torch.permute(img, (0, 2, 1, 3))
    img = torch.reshape(img, (C, row_num * H, col_num * W))
    img_pil = transforms.ToPILImage()(img)
    img_pil.save(file_path_save)