
import os
import _utils_file

def get_image_file_time(img_file_path):
    img_file_path = _utils_file.check_file_exist(img_file_path)
    unix_stamp_modify = os.path.getmtime(img_file_path) # last modified time
    unix_stamp_create = os.path.getctime(img_file_path)
    return unix_stamp_create, unix_stamp_modify