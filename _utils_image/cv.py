from __future__ import annotations
from _utils_import import _utils_file
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy as np
    import cv2 # pip install opencv-python
else:
    np = DLUtils.LazyImport("numpy")
    cv2 = DLUtils.LazyImport("cv2")

def file_to_img(img_file_path, RaiseOnError=True) -> np.ndarray:
    # cv2.imread() is not used.
        # might have problem when file_path contains unicode characters.
    Stream = open(img_file_path, "rb")
    ImageBytes = bytearray(Stream.read())
    ImageNp = np.asarray(ImageBytes, dtype=np.uint8)
    if RaiseOnError:
        img_cv = cv2.imdecode(ImageNp, cv2.IMREAD_UNCHANGED)
        return img_cv
    try:
        img_cv = cv2.imdecode(ImageNp, cv2.IMREAD_UNCHANGED)
    except Exception:
        return None
    return img_cv # np.ndarray
file_to_img_cv = file_to_img

def resize_image(img_cv, width=None, height=None):
    height_origin = img_cv.shape[0]
    width_origin = img_cv.shape[1]
    if height is None or width is None:
        if height is not None:
            ratio = height / height_origin
            width = round(ratio * width_origin)
        elif width is not None:
            ratio = width / width_origin
            height = round(ratio * height_origin)
        else:
            raise ValueError
    img_resized_cv = cv2.resize(img_cv, (width, height), interpolation=cv2.INTER_AREA)
    return img_resized_cv

def resize_imgae_by_ratio(Image: np.ndarray, ratio:float) -> np.ndarray:
    height_origin = Image.shape[0]
    width_origin = Image.shape[1]
    assert isinstance(ratio, float) and ratio > 0.0
    Height = round(ratio * height_origin)
    Width = round(ratio * width_origin)        
    img_resized_cv = cv2.resize(Image, (Width, Height), interpolation=cv2.INTER_AREA)
    return img_resized_cv

def img_to_file(img_cv: np.ndarray, file_path_save, format=None):
    # cv2.imwrite() is not used here.
        # might have problem when FilePath contains unicode characters.
        # result = cv2.imwrite(file_path_save, img_cv)

    if format is None:
        file_path_save_no_suffix, suffix = _utils_file.get_file_path_and_suffix(file_path_save)
        if suffix is None:
            format = "png"
        else:
            format = suffix
        format = format.lower()
    else:
        assert isinstance(format, str)
        format = format.lower()
    format = format.lstrip(".")

    # convert to jpeg and save in variable
    img_bytes = cv2.imencode("." + format, img_cv)[1].tobytes()
        # note that cv2(opencv) uses bgr not rgb.

    _utils_file.create_dir_for_file_path(file_path_save)
    with open(file_path_save, 'wb') as f:
        f.write(img_bytes)
    return True
img_cv_to_file = img_to_file

def compress_image_by_resize(img_file_path, file_path_save=None, ratio:float=None):
    if file_path_save is None:
        file_path_no_suffix, suffix = _utils_file.get_file_path_and_suffix(img_file_path)
        file_path_save = file_path_no_suffix + "-compressed" + "." + suffix
    img_cv = file_to_img_cv(img_file_path)
    assert not _utils_file.file_exist(file_path_save)
    assert ratio is not None

    width_origin, height_origin = img_cv.shape[1], img_cv.shape[0]
    
    import math
    ratio_1d = math.sqrt(ratio)
    width = round(width_origin * ratio_1d)
    height = round(height_origin * ratio_1d)

    img_compressed_cv = resize_image(img_cv, width=width, height=height)
    img_to_file(img_compressed_cv, file_path_save)