
from _utils_import import np, Im, plt, cv2

def img_pil_to_np_array(img_pil):
    return np.array(img_pil)

def np_array_to_img_pil(img_np):
    img_pil = Im.fromarray(img_np)
    return img_pil

def image_file_to_np_array_float01(file_path, backend:str="pil"):
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

def image_file_to_png(file_path, file_path_save=None, backend="pil", keep_exif=True):
    backend = backend.lower()
    if backend in ["pil"]:
        from .pil import image_file_to_png
        image_file_to_png(file_path, file_path_save, keep_exif=keep_exif)
    else:
        raise NotImplementedError

def image_file_to_jpg(file_path, file_path_save=None, quality:int=90, backend="pil"):
    backend = backend.lower()
    if backend in ["pil"]:
        from .pil import image_file_to_jpg as image_file_to_jpg_pil
        image_file_to_jpg_pil(file_path, file_path_save, quality)
    else:
        raise NotImplementedError

def avif_to_jpg(file_path, file_path_save=None, quality:int=90, backend="pil"):
    backend = backend.lower()
    if backend in ["pil"]:
        return read_image_file_pil(file_path=file_path, file_path_save=file_path_save, quality=quality)
    else:
        raise NotImplementedError

def get_test_image_np_float01(name="lenna", backend="pil"):
    backend = backend.lower()
    import os
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    if name in ["lenna"]:
        file_path_img = dir_path_current + "image-test/" + "lenna.png"
    else:
        raise ValueError(name)
    if backend in ["cv", "cv2"]: # np means return numpy array
        img_np = read_image_file_cv(file_path_img)
        return img_np
    elif backend in ["pil"]:
        img_pil = file_to_image_np_float01(file_path_img)
        return img_pil
    else:
        raise NotImplementedError

def get_row_num_and_col_num(plot_num, row_num=None, col_num=None):
    if row_num is None:
        if col_num is None:
            if plot_num <= 3:
                return 1, plot_num
            col_num = round(plot_num ** 0.5)
            if col_num == 0:
                col_num = 1
            row_num = plot_num // col_num
            if plot_num % col_num > 0:
                row_num += 1
            return row_num, col_num
        else:
            row_num = plot_num // col_num
            if plot_num % col_num > 0:
                row_num += 1
            return row_num, col_num
    else:
        if col_num is None:
            col_num = plot_num // row_num
            if plot_num % row_num > 0:
                col_num += 1
            return row_num, col_num
        else:
            if plot_num != row_num * col_num:
                raise Exception('plot_num: %d != row_num %d x ColumnNum %d'%(plot_num, row_num, col_num))
            else:
                return row_num, col_num

from .pil import (
    import_pil_heif,
    file_to_image_np_int255,
    file_to_image_np_float01,
    image_np_float01_to_file,
    image_np_int255_to_file,
)
from .pil import read_image_file as read_image_file_pil

from .cv import ( # bgr, not rgb
    put_text_on_image,
    put_text_on_image_center,
    # image_np_float01_to_file,
    # image_np_int255_to_file,
)
from .cv import read_image_file as read_image_file_cv