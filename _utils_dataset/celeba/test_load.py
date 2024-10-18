
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

from _utils_import import _utils_io, _utils_file, Dict, torch
import _utils_dataset, _utils_torch, _utils_math

def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--epoch_num", type=int, default=5)
    parser.add_argument("--device", type=int, dest="device", default=None)
    parser.add_argument("--learning_rate", type=float, default=0.01)
    args, unknownargs = parser.parse_known_args()
    return Dict(args)

def main():
    args = get_args()

    # get mnist dataset
    dataset = _utils_dataset.CelebADataset().from_zip_file(
        file_path_zip="~/dataset/celeba/img_align_celeba.zip",
        dir_path_data="~/dataset/celeba/"
    )

    from torch.utils.data import DataLoader as TorchDataLoader
    from torch.utils.data import Dataset as TorchDataset
    train_data_loader = TorchDataLoader(
        dataset.get_dataset(), # should be compatible with torch.utils.data.Dataset
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=10
    )
    train_batch_num = _utils_torch.get_batch_num(train_data_loader)
    
    pipe_out = _utils_io.PipeOut()
    for train_epoch_index in range(args.epoch_num): # epoch loop
        TrainData = iter(train_data_loader)
        pipe_out.print("TrainEpoch %03d/%03d"%(train_epoch_index, args.epoch_num))
        with pipe_out.increased_indent():
            for train_batch_index in range(train_batch_num):
                image_batch = next(TrainData) # (batch_size, H, W, 3)
                pipe_out.print_every(100, "TrainBatch %03d/%03d"%(train_batch_index, train_batch_num))
        try:
            end = next(TrainData)
        except StopIteration: # check TrainData has been iterated to end
            pass
        else:
            raise Exception

    return

if __name__ == "__main__":
    main()