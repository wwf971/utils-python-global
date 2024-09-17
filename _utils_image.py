
import os
import _utils_file
from _utils_import import np, Im, plt, cv2
def get_image_file_time(img_file_path):
    img_file_path = _utils_file.check_file_exist(img_file_path)
    unix_stamp_modify = os.path.getmtime(img_file_path) # last modified time
    unix_stamp_create = os.path.getctime(img_file_path)
    return unix_stamp_create, unix_stamp_modify

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

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pillow_avif # pip3 install pillow-avif-plugin
else:
    Im = DLUtils.GetLazyPILImage()
    ExifTags = DLUtils.LazyFromImport("PIL", "ExifTags")
    pillow_avif = DLUtils.LazyImport("pillow_avif")

from .png import ImageFileToPng

def AvifToPng(FilePath, file_path_save=None):
    pillow_avif.__name__ # trigger lazy import
    return ImageFileToPng(FilePath, file_path_save=file_path_save)

def img_file_to_png_pil(file_path, file_path_save=None):
    img = Im.open(file_path)
    img = img.convert("RGB")
    # supported format: jpg, jfif, avif, webp.
        # .avif image requires pillow_avif
        # .heif image requires pillow_heif
    if file_path_save is None:
        file_path_save = _utils_file.change_file_path_suffix(file_path, ".png")
        file_path_save = DLUtils.EnsureFileDir(file_path_save)
    file_path_save = DLUtils.file.RenameFileIfExists(file_path_save)
    Image.save(file_path_save, "png")
    assert DLUtils.ExistsFile(file_path_save)
    return file_path_save
ToPngFile = ToPng = ImageFileToPng

def ImageFileToJpg(file_path, file_path_save=None):
    Image = Im.open(file_path).convert("RGB")
        # .avif image requires pillow_avif
        # .heif image requires pillow_heif
    if file_path_save is None:
        SavePath = _utils_file(FilePath, ".jpg")
        SavePath = DLUtils.EnsureFileDir(SavePath)
    SavePath = DLUtils.EnsureFileDir(SavePath)
    Image.save(SavePath, "jpeg",
        # subsampling=0,
        quality=50
    )
    return SavePath
ToJPGFile = ToJpgFile = ToJpg = ToJPG = ImageFileToJpg