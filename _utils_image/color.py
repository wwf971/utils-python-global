
from _utils_import import Dict
color_str_to_rgba_dict = Dict(
    red=(1.0, 0.0, 0.0, 1.0),
    green=(0.0, 1.0, 0.0, 1.0),
    blue=(0.0, 0.0, 1.0, 1.0),
)

def color_str_to_rgba_float01(color_str: str):
    color_str = color_str.lower()
    return

def color_float01_to_uint255(rgba_float01: tuple):
    color_float01 = []
    for channel in rgba_float01:
        assert 0.0 <= channel <= 1.0
        color_float01.append(round(255.0 * channel))
    return tuple(color_float01)