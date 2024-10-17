import struct
from _utils_import import _utils_file, np, Dict

dataset_dir_config = Dict({
    "files": {
        "train-images-idx3-ubyte": {
            "md5": "6bbc9ace898e44ae57da46a324031adb",
            "size": 47040016,
            "size_str": "44.861 MB"
        },
        "train-labels-idx1-ubyte": {
            "md5": "a25bea736e30d166cdddb491f175f624",
            "size": 60008,
            "size_str": "58.602 KB"
        },
        "t10k-images-idx3-ubyte": {
            "md5": "2646ac647ad5339dbf082846283269ea",
            "size": 7840016,
            "size_str": "7.477 MB"
        },
        "t10k-labels-idx1-ubyte": {
            "md5": "27ae3e4e09519cfbb04c329615203637",
            "size": 10008,
            "size_str": "9.773 KB"
        }
    },
    "dirs": {}
})

def _load_dataset_from_dir(path_info, check_integrity=False):
    if check_integrity:
        result = _utils_file.check_dir_config(
            path_info.dir_path_data, dataset_dir_config
        )
        if not result:
            raise Exception
    data = Dict(
        train_image = load_image(path_info.file_path_train_image),
        train_label = load_label(path_info.file_path_train_label), 
        test_image = load_image(path_info.file_path_test_image), 
        test_label = load_label(path_info.file_path_test_label), 
    )
    return data

def load_dataset_from_dir(dir_path, check_integrity=False):
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    path_info = Dict()
    path_info.update(
        file_path_train_image = dir_path + 'train-images-idx3-ubyte',
        file_path_train_label = dir_path + 'train-labels-idx1-ubyte',
        file_path_test_image = dir_path + 't10k-images-idx3-ubyte',
        file_path_test_label = dir_path + 't10k-labels-idx1-ubyte',
    )
    assert _utils_file.files_exist(
        path_info.file_path_train_image,
        path_info.file_path_train_label,
        path_info.file_path_test_image,
        path_info.file_path_test_label,
    )
    return _load_dataset_from_dir(path_info, check_integrity=check_integrity)

def load_dataset_from_zip_file(file_path_zip, use_cache=True, check_integrity=False):
    file_path_zip = _utils_file.file_path_to_unix_style(file_path_zip)
    dir_path_zip_file = _utils_file.get_dir_path_of_file_path(file_path_zip)
    dir_path_extract = dir_path_zip_file + "mnist/"
    dir_path_data = dir_path_extract

    path_info = Dict(file_path_zip=file_path_zip)
    path_info.dir_path_extract = dir_path_extract
    path_info.dir_path_data = path_info.dir_path_extract

    path_info.update(
        file_path_train_image = dir_path_data + 'train-images-idx3-ubyte',
        file_path_train_label = dir_path_data + 'train-labels-idx1-ubyte',
        file_path_test_image = dir_path_data + 't10k-images-idx3-ubyte',
        file_path_test_label = dir_path_data + 't10k-labels-idx1-ubyte',
    )
    if use_cache:
        # extract all 4 .gz files
        if _utils_file.files_exist(
            path_info.file_path_train_image,
            path_info.file_path_train_label,
            path_info.file_path_test_image,
            path_info.file_path_test_label,
        ):
            pass
        else:
            zip_file_to_gz_file(path_info)
            gz_file_to_data_file(path_info, remove_after_extract=True)

    assert _utils_file.files_exist(
        path_info.file_path_train_image,
        path_info.file_path_train_label,
        path_info.file_path_test_image,
        path_info.file_path_test_label,
    )

    return _load_dataset_from_dir(path_info, check_integrity=check_integrity)

def zip_file_to_gz_file(path_info: Dict):
    # input: path/to/mnist.zip
    # output: path/to/dir_extract/
        # t10k-images-idx3-ubyte.gz
        # t10k-labels-idx1-ubyte.gz
        # train-images-idx3-ubyte.gz
        # train-labels-idx1-ubyte.gz
    
    file_path_zip = path_info.file_path_zip


    dir_path_extract = path_info.dir_path_extract

    dir_path_extract = _utils_file.dir_path_to_unix_style(dir_path_extract)

    # check that all 4 required .gz files have been extracted
    path_info.update_if_not_exist(
        file_path_train_image_gz=dir_path_extract + 'train-images-idx3-ubyte.gz',
        file_path_train_label_gz=dir_path_extract + 'train-labels-idx1-ubyte.gz',
        file_path_test_image_gz=dir_path_extract + 't10k-images-idx3-ubyte.gz',
        file_path_test_label_gz=dir_path_extract + 't10k-labels-idx1-ubyte.gz',
    )

    _utils_file.extract_zip_file(file_path_zip, dir_path_extract)
    _utils_file.check_files_exist(
        path_info.file_path_train_image_gz,
        path_info.file_path_train_label_gz,
        path_info.file_path_test_image_gz,
        path_info.file_path_test_label_gz
    )
    return path_info

def gz_file_to_data_file(path_info: Dict, remove_after_extract=True):
    dir_path_data = path_info.dir_path_data

    # extract all 4 .gz files
    path_info.update_if_not_exist(
        file_path_train_image = dir_path_data + 'train-images-idx3-ubyte',
        file_path_train_label = dir_path_data + 'train-labels-idx1-ubyte',
        file_path_test_image = dir_path_data + 't10k-images-idx3-ubyte',
        file_path_test_label = dir_path_data + 't10k-labels-idx1-ubyte',
    )

    _utils_file.extract_gz_file(path_info.file_path_train_image_gz, path_info.file_path_train_image)
    _utils_file.extract_gz_file(path_info.file_path_train_label_gz, path_info.file_path_train_label)
    _utils_file.extract_gz_file(path_info.file_path_test_image_gz, path_info.file_path_test_image)
    _utils_file.extract_gz_file(path_info.file_path_test_label_gz, path_info.file_path_test_label)

    if remove_after_extract: # clean .gz files
        _utils_file.remove_files(
            path_info.file_path_train_image_gz,
            path_info.file_path_train_label_gz,
            path_info.file_path_test_image_gz,
            path_info.file_path_test_label_gz
        )
    return path_info

def load_image(FilePath):
    with open(FilePath, 'rb') as f:
        Buf = f.read()
    # read 4 integers from Buf
    magic_num, image_num, row_num, col_num = struct.unpack_from('>IIII', Buf, 0)
    bit_num = image_num * row_num * col_num
    # read image data from Buf
    image_list = struct.unpack_from('>' + str(bit_num) + 'B', Buf, struct.calcsize('>IIII'))
    image_list = np.reshape(image_list, [image_num, row_num * col_num]) # [60000, 784]
    # np.int64 -> np.uint8
    image_list = image_list.astype(np.uint8).reshape(-1, 28, 28)
    return image_list

def load_label(FilePath):
    with open(FilePath, 'rb') as f:
        Buf = f.read()
    # read 2 integer from Buf
    magic_num, data_num = struct.unpack_from('>II', Buf, 0) 
    # read label data from Buf
    label_list = struct.unpack_from('>' + str(data_num) + "B", Buf, struct.calcsize('>II'))
    label_list = np.reshape(label_list, [data_num])
    # np.int64 -> np.uint8
    label_list = label_list.astype(np.uint8)
    return label_list