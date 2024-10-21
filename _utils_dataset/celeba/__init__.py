from _utils_import import _utils_file, Dict, torch
import _utils_file, _utils
from _utils_image import image_file_to_np_array_float01

sample_num = 202599
image_height = 218
image_width = 178
image_channel_num = 3

class CelebADataset():
    def from_zip_file(self, file_path_zip, dir_path_data=None, check_integrity=False):
        self.file_path_zip = file_path_zip
        self.dir_path_data = load_dataset_from_zip_file(
            file_path_zip,
            dir_path_data=dir_path_data,
        )
        self._is_build = True
        return self
    def get_dataset(self, transform=None):
        return Dataset(
            self.dir_path_data + "img_align_celeba/",
            transform=transform
        )

class Dataset():
    def __init__(self, dir_path_img, transform=None):
        self.dir_path_img = dir_path_img
        global sample_num
        self.sample_num = sample_num
        self.transform = transform
    def __len__(self):
        return self.sample_num
    def __getitem__(self, index):
        file_name_image = "%06d.jpg"%(index + 1)
            # 000001.jpg <-- inedx=0
            # ...
            # 202599.jpg <-- index=202598
        img_np = image_file_to_np_array_float01(self.dir_path_img + file_name_image)
        img_tensor = torch.from_numpy(img_np).permute(2, 0, 1)

        if self.transform is not None:
            img_transformed = self.transform(img_tensor)
            return img_transformed
        else:
            return img_np

def load_dataset_from_zip_file(file_path_zip, dir_path_data=None, use_cache=True):
    file_path_zip = _utils_file.file_path_to_unix_style(file_path_zip)
    dir_path_zip_file = _utils_file.get_dir_path_of_file_path(file_path_zip)

    if dir_path_data is not None:
        dir_path_data = _utils_file.dir_path_to_unix_style(dir_path_data)
        dir_path_extract = dir_path_data
    else:
        dir_path_data = dir_path_zip_file + "celeba/"
        dir_path_data = dir_path_extract

    sig_use_cache = False
    if use_cache:
        if _utils_file.dir_exist(dir_path_extract):
            if _utils_file.files_exist(
                dir_path_extract + "img_align_celeba/000001.jpg", # first image
                dir_path_extract + "img_align_celeba/202599.jpg", # last image
            ):
                sig_use_cache = True
    if not sig_use_cache:
        _utils_file.extract_zip_file(
            file_path_zip, dir_path_extract
        )
    return dir_path_extract