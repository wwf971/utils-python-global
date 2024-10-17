from __future__ import annotations
import _utils_import
from _utils_import import _utils_file
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy as np
    import cv2 # pip install opencv-python
else:
    np = _utils_import.lazy_import("numpy")
    cv2 = _utils_import.lazy_import("cv2")

def read_image_file(img_file_path, RaiseOnError=True) -> np.ndarray:
    # cv2.imread() is not used.
        # might have problem when file_path contains unicode characters.
    Stream = open(img_file_path, "rb")
    ImageBytes = bytearray(Stream.read())
    img_np = np.asarray(ImageBytes, dtype=np.uint8)
    if RaiseOnError:
        img_cv = cv2.imdecode(img_np, cv2.IMREAD_UNCHANGED)
        return img_cv
    try:
        img_cv = cv2.imdecode(img_np, cv2.IMREAD_UNCHANGED)
    except Exception:
        return None
    return img_cv # np.ndarray
file_to_img_cv = file_to_img = read_image_file

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

def resize_image_by_ratio(Image: np.ndarray, ratio:float) -> np.ndarray:
    height_origin = Image.shape[0]
    width_origin = Image.shape[1]
    assert isinstance(ratio, float) and ratio > 0.0
    Height = round(ratio * height_origin)
    Width = round(ratio * width_origin)        
    img_resized_cv = cv2.resize(Image, (Width, Height), interpolation=cv2.INTER_AREA)
    return img_resized_cv


def image_np_float01_to_file(img_np: np.ndarray, file_path_save, format=None):
    return image_np_int255_to_file(img_np * 255.0, file_path_save, format)

def image_np_int255_to_file(img_np: np.ndarray, file_path_save, format=None):
    # cv2.imwrite() is not used here.
        # might have problem when FilePath contains unicode characters.
        # result = cv2.imwrite(file_path_save, img_np)

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

    img_bytes = cv2.imencode("." + format, img_np)[1].tobytes()
        # note that cv2(opencv) uses bgr not rgb.

    _utils_file.create_dir_for_file_path(file_path_save)
    with open(file_path_save, 'wb') as f:
        f.write(img_bytes)
    return True

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


def put_text_on_image_center(image: np.ndarray, text="Text", text_box_width=None, text_box_height=None, color=(0, 0, 0)):
    img_height, img_width = image.shape[0], image.shape[1]
    
    if text_box_width is None and text_box_height is None:
        text_box_width = round(img_width * 0.5)
        text_box_height = round(img_height * 0.5)

    # get text_box width and height, if font_scale=1.0
    font_scale = 1.0
    size = cv2.getTextSize(
        text=text,
        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
        fontScale=font_scale,
        thickness=3
    ) # ((width, height), ?)

    width_current = size[0][0]
    height_current = size[0][1]
    
    # adjust font_scale, to make text centered on image
    font_scale = font_scale * min(text_box_width / width_current, text_box_height / height_current)

    size = cv2.getTextSize(
        text=text,
        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
        fontScale=font_scale,
        thickness=3
    ) # ((width, height), ...)

    width_current = size[0][0]
    height_current = size[0][1]
    
    x_left = round(img_width / 2.0 - width_current / 2.0)
    y_bottom = round(img_height / 2.0 + height_current / 2.0)

    put_text_on_image(image, text, x_left, y_bottom, color, font_scale)

def put_text_on_image(image: np.ndarray, text="Text", x_left=0, y_bottom=0, color=(0, 0, 0), font_scale=1.0):
    cv2.putText(
        img=image,
        text=text,
        org=(x_left, y_bottom), # coordinate of left bottom corner
        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
        fontScale=font_scale,
        color=color,
        thickness=3
    )
    return image