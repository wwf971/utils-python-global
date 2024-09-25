
import os
import _utils_file
from _utils_import import Im

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pillow_avif # pip3 install pillow-avif-plugin
else:
    Im = DLUtils.GetLazyPILImage()
    ExifTags = _utils_import.LazyFromImport("PIL", "ExifTags")
    pillow_avif = _utils_import.LazyImport("pillow_avif")

def img_file_to_png_pil(file_path, file_path_save=None):
    backend = backend.lower()
    img_pil = Im.open(file_path)
    img_pil = img_pil.convert("RGB")
    # supported format: jpg, jfif, avif, webp.
        # .avif image requires pillow_avif
        # .heif image requires pillow_heif
    if file_path_save is None:
        file_path_save = _utils_file.change_file_path_suffix(file_path, ".png")
    assert not _utils_file.is_same_file(file_path, file_path_save) # avoid overwriting original image file
    # assert not _utils_file.file_exist(file_path_save)
    img_pil.save(file_path_save, "png")
    assert _utils_file.file_exist(file_path_save)
    return file_path_save

def avif_to_png_pil(file_path, file_path_save=None):
    pillow_avif.__name__ # trigger lazy import
    return img_file_to_png(file_path, file_path_save=file_path_save)

def img_file_to_jpg_pil(file_path, file_path_save=None, quality:int=100):
    # quality: affects compression rate. jpeg images themselves don't have quality.
        # range: [0, 100]
        # 100: almost no loss.
        # 90: good quality and siganificant compression.
    img_pil = Im.open(file_path).convert("RGB")
        # .avif image requires pillow_avif
        # .heif image requires pillow_heif
    if file_path_save is None:
        file_path_save = _utils_file.change_file_path_suffix(file_path, ".jpg")
    assert not _utils_file.is_same_file(file_path, file_path_save) # avoid overwriting original image file
    img_pil.save(file_path_save, format="jpeg",
        subsampling=0, # chroma subsampling. set to 0 to make image look sharper.
        quality=quality 
    )
    assert _utils_file.file_exist(file_path_save)
    return file_path_save