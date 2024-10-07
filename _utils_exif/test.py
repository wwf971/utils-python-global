
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

import _utils_exif

def unit_test_1():
    file_path_img = r"Z:\待处理\←icloud\Image20220221_04340200.jpg"
    # file_path_img = r"D:\Downloads\Image20220221_04340200.jpg"
    from _utils_exif.piexif import get_exif_dict as get_exif_dict_piexif
    from _utils_exif.pil import get_exif_dict as get_exif_dict_pil

    exif_dict_piexif = get_exif_dict_piexif(file_path_img)
    exif_dict_exif = get_exif_dict_pil(file_path_img)
    # dict_keys(['0th', 'Exif', 'GPS', 'Interop', '1st', 'thumbnail'])

def unit_test_2():
    img_file_path = r"Z:\待处理\←icloud\Image20220221_04340200.jpg"
    # img_file_path = r"D:\Downloads\Image20220221_04340200.jpg"
    exif_dict = _utils_exif.piexif.get_exif_dict(img_file_path)
    exif_dict_pil = _utils_exif.pil.get_exif(img_file_path)
    # dict_keys(['0th', 'Exif', 'GPS', 'Interop', '1st', 'thumbnail'])
    from _utils_file import get_file_create_unix_stamp, get_file_modify_unix_stamp
    from _utils_time import unix_stamp_to_time_str
    unix_stamp_create = get_file_create_unix_stamp(img_file_path)
    unix_stamp_modify = get_file_modify_unix_stamp(img_file_path)

    time_str_create = unix_stamp_to_time_str(unix_stamp_create)
    time_str_modify = unix_stamp_to_time_str(unix_stamp_modify)

    print(
        "create: %s\nmodify: %s"%(time_str_create, time_str_modify)
    )

if __name__ == "__main__":
    unit_test()