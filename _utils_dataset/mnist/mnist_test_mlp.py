from __future__ import annotations
"""
this script tests mnist dataset
"""

"""
experiment result:
    learning_rate = 0.001.
        <20.0% train_acc in 5 epoch
    learning_rate = 0.01.
        60.0%~80.0% train_acc in 5 epoch
"""
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

from _utils_import import _utils, _utils_file, _utils_io, Dict
import _utils_torch, _utils_math, _utils_dataset
from _utils_torch import MLP, torch_module_from_file

def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--epoch_num", type=int, default=5)
    parser.add_argument("--device", type=int, dest="device", default=None)
    parser.add_argument("--learning_rate", type=float, default=0.01)
    args, unknownargs = parser.parse_known_args()
    return Dict(args)

def main(base_dir_path=None):
    import _utils_file, _utils_math
    from _utils_train import (
        FloatLog, IntLog,
        TriggerFuncAtEveryFixedInterval
    )
    import torch
    import torch.nn as nn
    import numpy as np
    args = get_args()
    if args.device is None:
        import _utils_gpu
        device = _utils_torch.get_device_with_largest_available_useage()
    else:
        device = args.device

    if base_dir_path is None:
        base_dir_path = _utils_file.get_file_path_no_suffix(__file__) + "/"
    base_dir_path = _utils_file.create_dir_if_not_exist(base_dir_path)

    # create model
    model = MLP().init(28 * 28, 50, 10).build()
    save_file_path = base_dir_path + "model.dat"
    model.to_file(save_file_path).clear()
    model = torch_module_from_file(save_file_path).build()
    
    # test model
    x = _utils_math.sample_from_gaussian_01((64, 28 * 28))
    x = _utils_torch.np_array_to_torch_tensor(x).float()
    y = model.forward(x)
    model.to(device)
    
    optimizer = torch.optim.SGD(
        model.parameters(), # list-like
        lr=args.learning_rate, # required
        momentum=0.1, # default: 0.0
        dampening=0.0, # default: 0.0
        nesterov=True # default: False
    )

    # get mnist dataset
    dataset = _utils_dataset.MNISTDataset().from_zip_file("~/dataset/mnist.zip")
    
    # simulate train
    import torch
    from torch.utils.data import DataLoader as TorchDataLoader
    from torch.utils.data import Dataset as TorchDataset
    train_data_loader = TorchDataLoader(
        dataset.get_train_set(), # should be compatible with torch.utils.data.Dataset
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0
    )
    train_batch_num = _utils_torch.get_batch_num(train_data_loader)
    import _utils_io
    
    pipe_out = _utils_io.PipeOut()
    report_batch_num = round(train_batch_num / 3.0)
    log_loss = FloatLog(report_batch_num)
    log_acc = IntLog(report_batch_num)
    context = Dict()
    reporter = TriggerFuncAtEveryFixedInterval(
        interval=report_batch_num, 
        func=lambda : pipe_out.print("Epoch%03d Batch%03d/%03d Acc: %.3f Loss: %.3f"%(
            context.epoch_index,
            context.batch_index,
            context.batch_num,
            log_acc.report_avg(),
            log_loss.report_avg()
        ))
    )

    for train_epoch_index in range(args.epoch_num):
        train_data = iter(train_data_loader)
        pipe_out.print("TrainEpoch %d"%train_epoch_index)
        with pipe_out.increased_indent():
            context.epoch_index = train_epoch_index
            for train_batch_index in range(train_batch_num):
                context.batch_index = train_batch_index
                context.batch_num = train_batch_num
                train_data_batch = next(train_data)
                image, class_index_truth = train_data_batch # float32. range: [0.0, 1.0]
                image, class_index_truth = image.to(device), class_index_truth.to(device).long()
                batch_size = image.shape[0]
                model.zero_grad()
                class_logit = model.forward(
                    image.reshape(batch_size, -1) # (28, 28)
                ) # (batch_size, ClassNum)
                loss = torch.nn.functional.cross_entropy(
                    class_logit, # (batch_size, ClassNum)
                    class_index_truth # (batch_size)
                )
                loss.backward() # calculate gradient
                optimizer.step()
                class_index_pred = torch.argmax(
                    class_logit,
                    dim=1 # along which dimension to compute argmax. this dimension will be reduced after compute.
                ) # (batch_size)
                is_pred_correct = (class_index_pred == class_index_truth) # (BatchSize)
                
                log_loss.append(loss.item(), batch_size)
                log_acc.append(is_pred_correct.sum(), batch_size)
                reporter.tick()
                # pipe_out.print_every(100, "TrainBatch %d"%train_batch_index)
        try:
            end = next(train_data)
        except StopIteration: # check TrainData has been iterated to end
            pass
        else:
            raise Exception()
    return

if __name__ == "__main__":
    main()