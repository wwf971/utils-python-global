import _utils_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy as np
else:
    from DLUtils import np
if TYPE_CHECKING:
    import pynvml
else:
    pynvml = _utils_import.LazyImport("pynvml")

def ReturnGPUDevice(GPUIndex, ReturnType="str"):
    if ReturnType in ["str"]:
        return "cuda:%d"%GPUIndex
    elif ReturnType in ["int"]:
        return GPUIndex
    else:
        raise Exception()

def get_gpu_free_memory(gpu_index):
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    return info.free

def get_gpu_with_largest_available_memory(Verbose=False, ReturnType="str", OutPipe=None):
    import torch
    gpu_num = torch.cuda.device_count()
    MemoryFreeLargestIndex = -1
    MemoryFreeLargest = -1
    for gpu_index in range(gpu_num):
        MemoryFree = get_gpu_free_memory(gpu_index)
        if Verbose:
            print("GPU%d MemoryAvailable: %d"%(gpu_index, MemoryFree), file=OutPipe, flush=True)
        if MemoryFree > MemoryFreeLargest:
            MemoryFreeLargestIndex = gpu_index
            MemoryFreeLargest = MemoryFree
    if Verbose:
        print("gpu-%d has largest available memory %d"%(MemoryFreeLargestIndex, MemoryFreeLargest), file=OutPipe, flush=True)
    return ReturnGPUDevice(MemoryFreeLargestIndex, ReturnType=ReturnType)
get_gpu_with_largest_free_memory = get_gpu_with_largest_available_memory

try:
    import nvidia_smi # pip install nvidia-ml-py3
except Exception:
    IsNvidiaSmiImported = True
else:
    IsNvidiaSmiImported = False

def GPUDeviceInSpecifiedType(GPUIndex, Type="str"):
    if Type in ["str", "Str"]:
        return "cuda:%d"%GPUIndex
    elif Type in ["int", "Int"]:
        return GPUIndex
    else:
        raise Exception()

def GetGPUWithLargestAvailableUseage(ReturnType="str", Verbose=False):
    # assert IsNvidiaSmiImported
    nvidia_smi.nvmlInit()
    GPUNum = nvidia_smi.nvmlDeviceGetCount()
    GPUUseageList = []
    for GPUIndex in range(GPUNum):
        GPUHandle = nvidia_smi.nvmlDeviceGetHandleByIndex(GPUIndex)
        GPUUtil = nvidia_smi.nvmlDeviceGetUtilizationRates(GPUHandle)
        GPUUseageCurrent = GPUUtil.gpu / 100.0
        GPUUseageList.append(GPUUseageCurrent)
        if Verbose:
            print("GPU %d Useage: %.3f%%"%(GPUIndex, GPUUseageCurrent * 100.0))
    GPUUseageMinIndex = np.argmin(GPUUseageList)
    return GPUDeviceInSpecifiedType(GPUUseageMinIndex, Type=ReturnType)