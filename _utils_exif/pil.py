# 基于pillow库实现的一系列图片文件exif信息处理相关函数
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]
import _utils_import
from _utils_import import _utils_io, _utils_file, _utils_image, Im
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from PIL import ExifTags
    import pillow_heif
    pillow_heif.register_heif_opener() # essential for reading heif image
else:
    Im = _utils_import.lazy_import("PIL.Image", after_import=lambda module:module.import_pil_heif())
    ExifTags = _utils_import.lazy_from_import("PIL", "ExifTags")

def has_exif_info(img_file_path):
    img_pil = Im.img_file_path
    return "exif" in img_pil.info

def get_exif_dict(img_file_path):
    # from _utils_image.pil import import_pil_heif
    # import_pil_heif()
    img_pil = Im.open(img_file_path)
    img_pil.verify()
    img_pil = Im.open(img_file_path) # reopen after verify()
    exif_info = img_pil.getexif()
    return exif_info

def print_exif(img_file_path: str, out_pipe=None):
    if out_pipe is None:
        out_pipe = _utils_io.PipeOut()
    img_file_path = _utils_file.check_file_exist(img_file_path)
    exif_dict = get_exif_dict(img_file_path)
    if exif_dict is None:
        print("exif_dict: None")
    else:
        if len(exif_dict) == 0:
            return print("ImageWithExifInfo is empty.")
        for key, value in exif_dict.items():
            # print("key: %s Value: %s", key, value)
            if key in ExifTags.TAGS:
                out_pipe.print(f'{ExifTags.TAGS[key]}({key}):{value}')
            else:
                out_pipe.print(f'{key}: {value}')

def get_geo_tag(exif_info):
    GetTagDict = {}
    gps_keys = [
        'GPSVersionID','GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude',
        'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp', 'GPSSatellites', 'GPSStatus', 'GPSMeasureMode',
        'GPSDOP', 'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack', 'GPSImgDirectionRef',
        'GPSImgDirection', 'GPSMapDatum', 'GPSDestLatitudeRef', 'GPSDestLatitude', 'GPSDestLongitudeRef',
        'GPSDestLongitude', 'GPSDestBearingRef', 'GPSDestBearing', 'GPSDestDistanceRef', 'GPSDestDistance',
        'GPSProcessingMethod', 'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential'
    ]

    for key, value in exif_info.items():
        try:
            GetTagDict[gps_keys[key]] = str(value)
        except IndexError:
            pass
    return GetTagDict

def get_geo_info(img_file_path):
    exif_info = get_exif(img_file_path)
    geo_info = exif_info.get_ifd(0x8825)
    geo_info_dict = get_geo_tag(geo_info)
    return geo_info_dict

def print_geo_info(img_file_path):
    geo_info_dict = get_geo_info(img_file_path)
    for key, value in geo_info_dict.items():
        print(f'{key}:{value}')