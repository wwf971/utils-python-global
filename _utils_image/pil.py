from __future__ import annotations
import _utils_import
from _utils_import import _utils_io, _utils_file, Im, np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pillow_avif # pip3 install pillow-avif-plugin
else:
    ExifTags = _utils_import.lazy_from_import("PIL", "ExifTags")
    pillow_avif = _utils_import.lazy_import("pillow_avif")

def read_image_file(file_path):
    _, suffix = _utils_file.get_file_name_and_suffix(file_path)
    suffix = suffix.lower()
    if suffix in ["heic", "heif"]:
        import_pil_heif()
    if suffix in ["avif"]:
        import_pil_avif()
    img_pil = Im.open(file_path)
    return img_pil
file_to_img_pil = file_to_img = read_image_file

def file_to_image_np_int255(file_path):
    img_pil = read_image_file(file_path)
    return np.array(img_pil)

def file_to_image_np_float01(file_path):
    img_np_int255 = file_to_image_np_int255(file_path)
    return img_np_int255 / 255.0

def image_file_to_png(file_path, file_path_save=None, keep_exif=True):
    img_pil = Im.open(file_path)
    img_pil = img_pil.convert("RGB")
    # supported format: jpg, jfif, avif, webp.
        # .avif image requires pillow_avif
        # .heif image requires pillow_heif
    if file_path_save is None:
        file_path_save = _utils_file.change_file_path_suffix(file_path, ".png")
    assert not _utils_file.is_equiv_file_path(file_path, file_path_save) # avoid overwriting original image file
    # assert not _utils_file.file_exist(file_path_save)

    if keep_exif:
        import _utils_exif
        exif_dict = _utils_exif.piexif.get_exif_dict(img_pil=img_pil)
        _utils_exif.piexif.img_pil_and_exif_to_file(
            img_pil, exif_dict, file_path_save,
            format="png"
        )
    else:
        img_pil.save(file_path_save, "png")
        assert _utils_file.file_exist(file_path_save)
    return file_path_save

def png_to_jpg(file_path, file_path_save, quality=90):
    _utils_file.check_file_suffix(file_path)
    image_file_to_jpg(file_path, file_path_save, quality=quality, keep_exif=True)

def image_file_to_jpg(file_path, file_path_save=None, quality:int=100, keep_exif=True):
    # quality: affects compression rate. jpeg images themselves don't have quality.
        # range: [0, 100]
        # 100: almost no loss.
        # 90: good quality and siganificant compression.
    img_pil = Im.open(file_path).convert("RGB")
        # .avif image requires pillow_avif
        # .heif image requires pillow_heif

    if file_path_save is None:
        file_path_save = _utils_file.change_file_path_suffix(file_path, ".jpg")
    assert not _utils_file.is_equiv_file_path(file_path, file_path_save) # avoid overwriting original image file

    if keep_exif:
        import _utils_exif
        exif_dict = _utils_exif.piexif.get_exif_dict(img_pil=img_pil)
        _utils_exif.piexif.img_pil_and_exif_to_file(
            img_pil, exif_dict, file_path_save,
            format="jpeg", subsampling=0, quality=quality
        )
    else:
        img_pil.save(file_path_save, format="jpeg",
            subsampling=0, # chroma subsampling. set to 0 to make image look sharper.
            quality=quality
        )

    assert _utils_file.file_exist(file_path_save)
    return file_path_save

def avif_to_png(file_path, file_path_save=None):
    pillow_avif.__name__ # trigger lazy import
    return image_file_to_png(file_path, file_path_save=file_path_save)

def image_np_int255_to_file(image_np: np.ndarray, file_path_save):
    # image_np: uint8. range: [0, 255]
    img_pil = Im.fromarray(image_np)
    _utils_file.create_dir_for_file_path(file_path_save)
    img_pil.save(file_path_save)

def image_np_float01_to_file(image_np: np.ndarray, file_path_save):
    return image_np_int255_to_file((image_np * 255.0).astype(np.uint8), file_path_save)

def import_pil_avif():
    pillow_avif.__name__ # trigger lazy import

is_pillow_heif_imported = False
def import_pil_heif():
    """
        to deal with .HEIC images using PIL, you need to
            pip install pillow_heif
            pillow_heif.register_heif_opener()
    """
    # pillow_heif = _utils_import.lazy_import("pillow_heif", FuncAfterImport=lambda module:module.register_heif_opener())
    global is_pillow_heif_imported
    if not is_pillow_heif_imported:
        import pillow_heif as _pillow_heif # pip install pillow_heif
        global pillow_heif
        pillow_heif = _pillow_heif
        pillow_heif.register_heif_opener()
        is_pillow_heif_imported = True

def print_heic_exif(file_path_heic: str):
    import _utils_exif
    _utils_exif.piexif.print_exif(file_path_heic)

def heic_to_jpg(
    file_path_heic, file_path_save=None,
    quality=90, # jpg compress quality
    pipe_out=None,
    keep_exif=True,
    verbose=False
):
    if file_path_save is None:
        file_path_save = _utils_file.change_file_path_suffix("jpg")
    import _utils_exif.piexif as utils_exif_piexif
    
    _utils_file.check_file_exist(file_path_heic)
    file_path_heic = _utils_file.file_path_to_unix_style(file_path_heic)
    img_pil = Im.open(file_path_heic)
    
    exif_dict = utils_exif_piexif.get_exif_dict(img_pil=img_pil)
    if verbose:
        if pipe_out is None:
            pipe_out = _utils_io.PipeOut()
        pipe_out.print("BEFORE:")
        with pipe_out.increased_indent():
            utils_exif_piexif.print_exif(exif_dict)
    utils_exif_piexif.img_pil_and_exif_to_file(
        img_pil, exif_dict, file_path_save,
        format="jpeg", quality=quality
    )
    if verbose:
        from _utils_exif.piexif import ExifInfo
        img_pil_after = Im.open(file_path_save)
        exif_info_after = ExifInfo(img_pil=img_pil_after)
        pipe_out.print("AFTER:")
        with pipe_out.increased_indent():
            exif_info_after.print_exif_origin(pipe_out)

def heic_to_png(
    file_path_heic, file_path_save=None,
    quality=90, # jpg compress quality
    keep_exif=True,
):
    if file_path_save is None:
        file_path_save = _utils_file.change_file_path_suffix("png")
    import _utils_exif.piexif as utils_exif_piexif
    _utils_file.check_file_exist(file_path_heic)
    file_path_heic = _utils_file.file_path_to_unix_style(file_path_heic)
    img_pil = Im.open(file_path_heic)
    
    exif_dict = utils_exif_piexif.get_exif_dict(img_pil=img_pil)
    utils_exif_piexif.img_pil_and_exif_to_file(
        img_pil, exif_dict, file_path_save,
        format="png", quality=quality
    )