"""
This script tests mnist dataset
"""
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

from _utils_import import _utils_file, _utils_io, Dict
import _utils_torch, _utils_math, _utils_dataset

def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, dest="batch_size", default=64)
    parser.add_argument("--epoch_num", type=int, dest="epoch_num", default=5)
    args, unknownargs = parser.parse_known_args()
    return Dict(args)

def main(base_dir_path=None):
    args = get_args()
    if base_dir_path is None:
        base_dir_path = _utils_file.get_file_path_no_suffix(__file__) + "/"
    _utils_file.create_dir_if_not_exist(base_dir_path)

    # load dataset file
    dataset = _utils_dataset.MNISTDataset().from_zip_file(
        file_path_zip="~/dataset/mnist/mnist.zip",
        dir_path_data="~/dataset/mnist/"
    )

    """
    plot_image_example:
        visually check image direction.
        visually check image content corresponds to label.
            image label is in image file name.
    """
    _utils_file.clear_dir(base_dir_path + "exmaple-image/")
    dataset.plot_image_example(dir_path_save=base_dir_path + "exmaple-image/")
    
    # simulate train
    TrainSet = dataset.get_train_set()
    TestSet = dataset.get_test_set()
    print("mnist train_set. sample num: %d"%len(TrainSet))
    print("mnist test_set.  sample num: %d"%len(TestSet))

    from torch.utils.data import DataLoader as TorchDataLoader
    from torch.utils.data import Dataset as TorchDataset
    train_data_loader = TorchDataLoader(
        dataset.get_train_set(), # should be compatible with torch.utils.data.Dataset
        batch_size=args.batch_size
    )
    class_num = dataset.class_num
    train_batch_num = _utils_torch.get_batch_num(train_data_loader)
    pipe_out = _utils_io.PipeOut()

    for train_epoch_index in range(args.epoch_num): # epoch loop
        TrainData = iter(train_data_loader)
        pipe_out.print("TrainEpoch %03d/%03d"%(train_epoch_index, args.epoch_num))
        with pipe_out.increased_indent():
            for train_batch_index in range(train_batch_num):
                train_data_batch = next(TrainData)
                image, label = train_data_batch
                
                # check shape of Image data
                assert image.shape[1] == 28 and image.shape[2] == 28
                
                # check DLUtils.torch.ToOneHot is correct
                label_one_hot = _utils_torch.to_one_hot(label, class_num=class_num) # mnist has 10 class
                assert label_one_hot.shape[0] == label.shape[0]
                assert label_one_hot.shape[1] == class_num
                sample_index = _utils_math.random_int_in_range(0, label.shape[0])
                class_index_truth = label[sample_index]
                for class_index in range(class_num):
                    if class_index != class_index_truth:
                        assert label_one_hot[sample_index][class_index] == 0
                    else:
                        assert label_one_hot[sample_index][class_index] == 1
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