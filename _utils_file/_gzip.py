
import _utils_file
from _utils_import import shutil
import gzip
def extract_gz_file(file_path, file_path_save=None):
    """
        input: .gz file with file_path
        output: decompressed file with file_path_save
    """
    file_path = _utils_file.check_file_exist(file_path)
    if file_path_save is None:
        file_path_no_suffix, suffix = _utils_file.get_file_name_and_suffix(file_path)
        if suffix == "gz":
            file_path_save = file_path_no_suffix
            assert not _utils_file.file_exist(file_path_save)
        else:
            raise Exception
    file_path_save = _utils_file.create_dir_for_file_path(file_path_save)
    with gzip.open(file_path, 'rb') as file_in:
        with open(file_path_save, 'wb') as file_out:
            shutil.copyfileobj(file_in, file_out)
    return file_path_save

def is_gz_file(FilePath):
    with open(FilePath, 'rb') as test_f:
        return test_f.read(2) == b'\x1f\x8b' # .gz file magic number