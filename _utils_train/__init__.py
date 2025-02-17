import sqlite3
from _utils_import import torch, np
import _utils

from _utils_args import CustomArgumentParser
import random
def set_seed(seed: int=None, seed_random: int=None, seed_numpy: int=None, seed_torch: int=None):
    if seed_random is None and seed_numpy is None and seed_torch is None:
        seed_random = seed
        seed_numpy = seed
        seed_torch = seed

    if seed_random is not None:
        random.seed(seed_random)
    if seed_torch is not None:
        set_seed_for_torch(seed_torch)
    if seed_numpy is not None:
        set_seed_for_numpy(seed_numpy)

    return _utils.Dict()

def set_seed_for_numpy(seed: int):
    np.random.seed(seed)

def set_seed_for_torch(seed: int):
    torch.manual_seed(seed)

def get_device():
    import _utils_gpu
    if torch.cuda.is_available():
        return "cuda:%d"%_utils_gpu.get_gpu_with_largest_available_useage()
    else:
        return "cpu"

from ._tensorboard import (
    init_tensorboard,
    TensorboardWrapper
)

from .args import (
    save_args,
    Config
)

from .path import (
    get_model_file_path_by_epoch,
    set_dir_path_instance
)

from ._log import (
    IntLog,
    FloatLog,
    TriggerFuncAtEveryFixedInterval
)