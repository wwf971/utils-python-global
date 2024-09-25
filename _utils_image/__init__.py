
import os
import _utils_file
from _utils_import import np, Im, plt, cv2

def get_image_file_create_time(img_file_path):
    img_file_path = _utils_file.check_file_exist(img_file_path)
    unix_stamp_create = os.path.getctime(img_file_path) # create_time
    return unix_stamp_create

def get_image_file_modify_time(img_file_path):
    img_file_path = _utils_file.check_file_exist(img_file_path)
    unix_stamp_modify = os.path.getmtime(img_file_path) # last modified time
    return unix_stamp_modify

def img_file_to_np_array_float01(file_path, backend:str="PIL"):
    # return data type: float. value range: [0.0, 1.0]
    backend = backend.lower()
    if backend in ["im", "pil"]:
        img = Im.open(file_path)
        img = np.asarray(img) / 255.0
        if img is None: # some error occurs
            raise Exception
        return img
    elif backend in ["plt", "mpl", "matplotlib"]:
        img = plt.imread(file_path)
        raise not NotImplementedError
    elif backend in ["cv", "cv2", "opencv"]:
        # img = cv2.imread(FilePath)
        img = cv2.cv.LoadImage(file_path)
        raise not NotImplementedError
    else:
        raise not NotImplementedError

def img_file_to_png(file_path, file_path_save=None, backend="pil"):
    backend = backend.lower()
    if backend in ["pil"]:
        from .pil import img_file_to_png_pil
        img_file_to_png_pil(file_path, file_path_save)
    else:
        raise NotImplementedError

def img_file_to_jpg(file_path, file_path_save=None, quality:int=90, backend="pil"):
    backend = backend.lower()
    if backend in ["pil"]:
        from .pil import img_file_to_jpg_pil
        img_file_to_jpg_pil(file_path, file_path_save, quality)
    else:
        raise NotImplementedError