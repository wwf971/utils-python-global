import _utils_import
from _utils_import import np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pynvml
else:
    pynvml = _utils_import.lazy_import("pynvml")

def get_gpu_free_memory(gpu_index):
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    return info.free

def get_gpu_with_largest_available_useage(verbose=False, ReturnType="str", OutPipe=None) -> int:
    try:
        import torch
        gpu_num = torch.cuda.device_count()
        gpu_max_memory_index = -1
        MemoryFreeLargest = -1
        for gpu_index in range(gpu_num):
            MemoryFree = get_gpu_free_memory(gpu_index)
            if verbose:
                print("GPU%d MemoryAvailable: %d"%(gpu_index, MemoryFree), file=OutPipe, flush=True)
            if MemoryFree > MemoryFreeLargest:
                gpu_max_memory_index = gpu_index
                MemoryFreeLargest = MemoryFree
        if verbose:
            print("gpu-%d has largest available memory %d"%(gpu_max_memory_index, MemoryFreeLargest), file=OutPipe, flush=True)
        return gpu_max_memory_index
    except Exception:
        return 0

get_gpu_with_largest_free_memory = get_gpu_with_largest_available_useage

try:
    import nvidia_smi # pip install nvidia-ml-py3
except Exception:
    is_nvidia_smi_imported = True
else:
    is_nvidia_smi_imported = False

def GPUDeviceInSpecifiedType(GPUIndex, Type="str"):
    if Type in ["str", "Str"]:
        return "cuda:%d"%GPUIndex
    elif Type in ["int", "Int"]:
        return GPUIndex
    else:
        raise Exception

def get_gpu_with_largest_available_useage(ReturnType="str", Verbose=False) -> int:
    # assert is_nvidia_smi_imported
    try:
        nvidia_smi.nvmlInit()
        gpu_num = nvidia_smi.nvmlDeviceGetCount()
        gpu_useage_list = []
        for gpu_index in range(gpu_num):
            GPUHandle = nvidia_smi.nvmlDeviceGetHandleByIndex(gpu_index)
            GPUUtil = nvidia_smi.nvmlDeviceGetUtilizationRates(GPUHandle)
            GPUUseageCurrent = GPUUtil.gpu / 100.0
            gpu_useage_list.append(GPUUseageCurrent)
            if Verbose:
                print("GPU_%02d. Useage: %.3f%%"%(gpu_index, GPUUseageCurrent * 100.0))
        gpu_useage_min_index = np.argmin(gpu_useage_list)
        return gpu_useage_min_index
    except Exception:
        return 0