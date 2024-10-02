from __future__ import annotations
import _utils_file
import _utils_import
from _utils_import import Im, np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pillow_avif # pip3 install pillow-avif-plugin
else:
    ExifTags = _utils_import.LazyFromImport("PIL", "ExifTags")
    pillow_avif = _utils_import.LazyImport("pillow_avif")

def image_file_to_png(file_path, file_path_save=None):
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

def image_file_to_jpg(file_path, file_path_save=None, quality:int=100):
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

is_pillow_heif_imported = False
def import_pil_heif():
    """
        to deal with .HEIC images using PIL, you need to
            pip install pillow_heif
            pillow_heif.register_heif_opener()
    """
    # pillow_heif = _utils_import.LazyImport("pillow_heif", FuncAfterImport=lambda module:module.register_heif_opener())
    global is_pillow_heif_imported
    if not is_pillow_heif_imported:
        import pillow_heif as _pillow_heif # pip install pillow_heif
        global pillow_heif
        pillow_heif = _pillow_heif
        pillow_heif.register_heif_opener()
        is_pillow_heif_imported = True

def avif_to_png(file_path, file_path_save=None):
    pillow_avif.__name__ # trigger lazy import
    return image_file_to_png(file_path, file_path_save=file_path_save)

def image_np_int255_to_file(image_np: np.ndarray, file_path_save):
    # image_np: uint8. range: [0, 255]
    img_pil = Im.fromarray(image_np)
    _utils_file.create_dir_for_file_path(file_path_save)
    img_pil.save(file_path_save)

def ImageFloat01NpToFile(Image, FilePath):
    return ImageNp2File((Image * 255.0).astype(np.uint8), FilePath)
ImageFloat01NpToFile = ImageFloat01NpToFile