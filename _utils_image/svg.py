from typing import TYPE_CHECKING
import _utils_import
from _utils_import import _utils_file, _utils_image
if TYPE_CHECKING:
    import torchvision
    import cairosvg
else:
    torchvision = _utils_import.LazyImport("torchvision")
    cairosvg = _utils_import.LazyImport("cairosvg")

def svg_str_to_png(Str, file_path_save, scale=2.0):
    file_path_save = _utils_file.create_dir_for_file_path(file_path_save)
    cairosvg.svgToPng(bytestring=Str, write_to=file_path_save, scale=scale)
    return file_path_save

def svg_to_png(
        file_path_svg,
        file_path_save=None,
        scale=2.0 # spatial scale
    ):
    if file_path_save is None:
        file_path_save = _utils_file.change_file_path_suffix(file_path_svg, ".svg")
    svg_str = _utils_file.text_file_to_str(file_path_svg)
    file_path_save = svg_str_to_png(svg_str, file_path_save, scale=scale)
    return file_path_save

def svg_to_np_array_float01(file_path_svg, scale=2.0):
    svg_str = _utils_file.text_file_to_str(file_path_svg)

    file_path_temp = "output.png"
    file_path_temp = _utils_file.change_file_path_if_exist(file_path_temp)
    file_path_save = svg_to_png(file_path_svg, file_path_save=file_path_temp, scale=scale)
    img_np = _utils_image.img_file_to_np_array_float01(file_path_save)
    _utils_file.remove_file(file_path_temp)
    return img_np