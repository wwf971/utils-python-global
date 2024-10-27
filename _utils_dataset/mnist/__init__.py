import os
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
from _utils_import import _utils_file, torch, np
import _utils_file, _utils

class_num = 10
train_set_sample_num = 60000
test_set_sample_num = 10000
image_height = 28
image_width = 28

from .mnist_utils import (
    load_dataset_from_zip_file,
    load_dataset_from_dir
)

class MNISTDataset():
    def __init__(self, dir_path=None, file_path_zip=None):
        """
        mnist Dataset contains 50000 train images and 10000 test images.
        each image contains a hand-written digit in [0, 1...9]
        each image has size 28x28 pixels.
        each pixle has 1 color channel.
        """
        self._is_build = False
        if dir_path is not None:
            self.from_dir()
        elif file_path_zip is not None:
            self.from_zip_file()

        self.class_num = class_num
    def is_build(self):
        return self._is_build
    def from_zip_file(self, file_path_zip, dir_path_data=None, check_integrity=False):
        self.file_path_zip = file_path_zip
        self.data = load_dataset_from_zip_file(
            file_path_zip,
            dir_path_data=dir_path_data,
            check_integrity=check_integrity
        )
        self._is_build = True
        return self
    def from_dir(self, dir_path, check_integrity=False):
        self.dir_path = dir_path
        self.data = load_dataset_from_dir(dir_path, check_integrity=check_integrity)
        self._is_build = True
        return self
    def get_subset_list(self):
        return ("train", "test")
    def get_train_set(self, transform=None):
        assert self.is_build()
        return TrainSet(
            self.data.train_image,
            self.data.train_label,
            transform=transform
        )
    def get_test_set(self):
        assert self.is_build()
        return TestSet(
            self.data.test_image,
            self.data.test_label
        )
    def get_train_image(self, index=None):
        assert self.is_build()
        if index is None:
            return self.data.train_image[index]
        else:
            return self.data.train_image
    def get_train_label(self, index=None):
        assert self.is_build()
        if index is None:
            return self.data.train_label[index]
        else:
            return self.data.train_label
    def get_test_image(self, index=None):
        assert self.is_build()
        if index is None:
            return self.data.test_image[index]
        else:
            return self.data.test_image
    def get_test_label(self, index=None):
        assert self.is_build()
        if index is None:
            return self.data.test_label[index]
        else:
            return self.data.test_label
    def plot_image_example(self, index_list=None, plot_num=10, dir_path_save=None):
        """
        index [0, 600000) is train data.
        index [60000, 70000) is test data.
        """
        if dir_path_save is None:
            dir_path_save = dir_path_current
        _utils_file.create_dir_if_not_exist(dir_path_save)
        if index_list is None:
            import _utils_math
            index_list = _utils_math.multi_random_int_in_range_no_repeat(plot_num, 0, 70000)
        for index in index_list:
            if index >= 60000:
                dataset_type = "test"
                image = self.data.test_image[index - 60000]
                label = self.data.test_label[index - 60000]
            else:
                dataset_type = "train"
                image = self.data.train_image[index]
                label = self.data.train_label[index]
            
            # image: (28, 28), uint8.
            import _utils_image
            file_path_save = dir_path_save + "%s-%05d-class=%d.png"%(dataset_type, index, label) 
            _utils_image.image_np_int255_to_file(
                image, file_path_save
            )

class Dataset():
    """
    Pytorch framework requires torch.utils.data.Dataset to implement __len__ and __item__ method.
        __len__ tells how many data samples are in Dataset
        __item__ allows retrieving i-th sample by Dataset[i]
    """
    def __init__(self, image_list, label_list, transform=None):
        self.image_list = image_list
        self.label_list = label_list

        assert len(self.image_list) == len(self)
        assert len(self.label_list) == len(self)

        if transform is None:
            self.transform = lambda x:x
        else:
            self.transform = transform
    def __getitem__(self, index):
        # assert index < self.DataNum
        image_np = (self.image_list[index] / 255.0).astype(np.float32) # np.ndarray. shape: (32(height), 32(width))
            # data type: float32
            # value range: [0.0, 1.0]
        label = self.label_list[index]
        image = torch.from_numpy(image_np)
        image_transform = self.transform(image)
        return image_transform, label

class TrainSet(Dataset):
    def __len__(self):
        return train_set_sample_num

class TestSet(Dataset):
    def __len__(self):
        return test_set_sample_num

def get_statistics(dataset: MNISTDataset, file_path_save=None):
    stat = {
        "train": _utils.np_array_stat(
            _utils.to_np_array(dataset.get_train_image()) / 255.0
        ),
        "test": _utils.np_array_stat(
            _utils.to_np_array(dataset.get_test_image()) / 255.0
        ),
    }
    if file_path_save is None:
        file_path_save = _utils_file.get_file_path_current_no_suffix(__file__) + "mnist-statistics.jsonc"
    _utils.dict_to_json_file(stat, file_path_save)

if __name__ ==  "__main__":
    config = _utils_file.get_dir_config("~/dataset/mnist/")
    _utils.dict_to_json_file(config, dir_path_current + "mnist-dir-config.jsonc")

    # _utils_file.check_dir_config("~/dataset/mnist/", config)
    dataset = MNISTDataset().from_zip_file("~/dataset/mnist.zip", check_integrity=True)
    dir_path_plot = dir_path_current + "image-example/"
    _utils_file.clear_dir(dir_path_plot)
    dataset.plot_image_example(
        dir_path_save=dir_path_current + "image-example/"
    )
    pass
