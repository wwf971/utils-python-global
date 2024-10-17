

import zipfile
import _utils_file

def is_zip_file(file_path):
    return zipfile.is_zipfile(file_path)

def extract_zip_file(file_path_zip, dir_path_extract):
    """
        Extract .zip file to a folder.
    """
    file_path_zip = _utils_file.check_file_exist(file_path_zip)
    _utils_file.create_dir_if_not_exist(
        _utils_file.get_dir_path_of_dir_path(dir_path_extract)
    )
    with zipfile.ZipFile(file_path_zip, 'r') as zip_ref:
        zip_ref.extractall(dir_path_extract)
    return dir_path_extract