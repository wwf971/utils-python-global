# 基于piexif库实现的一系列图像exif相关函数
from __future__ import annotations
import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]
import _utils_import
from _utils_import import _utils_file, Im
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import piexif # pip install piexif
else:
    piexif = _utils_import.LazyImport("piexif")

class ExifInfo:
    def __init__(self, file_path_img=None, img_pil=None):
        if file_path_img is not None:
            self.from_img_file(file_path_img)
            self.file_path_img = file_path_img
        elif img_pil is not None:
            self.from_img_pil(img_pil)
    def from_img_file(self, file_path_img):
        self.exif_dict_origin = get_exif_dict(file_path_img)
        self.exif_dict = self.get_exif_dict()
        return self
    def from_img_pil(self, img_pil):
        self.exif_dict_origin = piexif.load(img_pil.info['exif'])
        self.exif_dict = self.get_exif_dict()
        return self
    def get_exif_dict(self):
        exif_dict = {}
        for category, subdict in self.exif_dict_origin.items():
            if subdict is not None:
                for key, value in subdict.items():
                    assert key not in exif_dict
                    exif_dict[key] = value
        return exif_dict
    def update_exif_dict(self):
        self.exif_dict = self.get_exif_dict()
        return self
    def items(self):
        return self.get_exif_dict().items()
    def is_empty(self):
        return len(self.get_exif_dict()) == 0
    def add_tag(self, key:int, value):
        add_exif_tag(self.exif_dict_origin, key, value)
        self.update_exif_dict()
    def get_tag(self, tag: int):
        if tag in self.exif_dict:
            return self.exif_dict[tag]
        else:
            return None
    def print_exif_origin(self, pipe_out=None):
        if pipe_out is None:
            import _utils_io
            pipe_out = _utils_io.PipeOut()
        pipe_out.print("exif_info:")
        for key, subdict in self.exif_dict_origin.items():
            with pipe_out.increased_indent():
                pipe_out.print("%s:"%key)
                with pipe_out.increased_indent():
                    if subdict is None:
                        continue
                    for key, value in subdict.items():
                        pipe_out.print("0x%04x(%05d): %s"%(int(key), int(key), value))
        return
    def print_exif(self, pipe_out=None):
        if pipe_out is None:
            import _utils_io
            pipe_out = _utils_io.PipeOut()
        pipe_out.print("exif_info:")
        with pipe_out.increased_indent():
            for key, value in self.items():
                pipe_out.print("0x%04x(%05d): %s"%(int(key), int(key), value))
        return
    def get_time(self):
        if 0x0132 in self.exif_dict:
            return self.exif_dict[0x0132] # "DateTime"
    def get_dict(self):
        return self.exif_dict_origin
        # exif_dict = {
        #     "0th":{
        #         0x0110: b"oneplus 10 pro" # 272(0x0110): model.(设备名称)
        #     },
        #     "Exif":{
        #     },
        #     "GPS":{},
        #     "Interop":{},
        #     "1st":{}
        # }
        # 存在的ExifCode会出现在ExifDict中的其中1个key下.
    def add_device_name(self, device_name: bytes):
        self.exif_dict_origin["0th"][0x0110] = device_name
            # b"wwf-oneplus" # device name
        self.update_exif_dict()
        return self
    def has_tag(self, tag: int):
        return tag in self.exif_dict
    def remove_tag(self, tag: int):
        assert self.has_tag(tag)
        self.remove_tag_if_exist()
    def remove_tag_if_exist(self, tag: int):
        for name, subdict in self.exif_dict_origin.items():
            if not isinstance(subdict, dict):
                continue
            # for _key, value in dict(subdict).items():
            #     if _key == tag:
            #         subdict.pop(_key)
            if tag in subdict:
                subdict.pop(tag)
        self.update_exif_dict()
        return self

class ImageWithExifInfo:
    def __init__(self, file_path_img=None):
        self.file_path_img = file_path_img
        img_pil = Im.open(file_path_img)
        self.exif_info = ExifInfo(img_pil=img_pil)
        self.img_pil = img_pil
    def to_file(self, file_path_save: str):
        exif_bytes = piexif.dump(self.exif_info.exif_dict_origin)
        assert not _utils_file.file_exist(file_path_save)
        self.img_pil.save(file_path_save, exif=exif_bytes) 
        return file_path_save
    to_img_file = to_file

def get_empty_exif_dict():
    # 图像文件不包含exif信息.
    return {
        "0th":{},
        "Exif":{},
        "GPS":{},
        "Interop":{},
        "1st":{},
        "thumbnail": None
    }

def img_pil_and_exif_to_file(img_pil:Im.Image, exif_dict=None, file_path_save=None, **kwargs):
    if exif_dict is None:
        exif_dict = get_empty_exif_dict()
    if 0xa301 in exif_dict['Exif'] and isinstance(exif_dict['Exif'][0xa301], int):
        # https://github.com/hMatoba/Piexif/issues/95
        exif_dict['Exif'][0xa301] = str(exif_dict['Exif'][0xa301]).encode('utf-8')
    exif_bytes = piexif.dump(exif_dict)
    img_pil.save(file_path_save, exif=exif_bytes, **kwargs)  
    return file_path_save

def print_exif(file_path_img=None, img_pil=None):
    # ExifInfo(file_path_img).print_exif()
    if file_path_img is not None:
        ExifInfo(file_path_img=file_path_img).print_exif_origin()
    elif img_pil is not None:
        ExifInfo(img_pil=img_pil).print_exif_origin()
    else:
        raise Exception

def add_exif_gps_tag(exif_dict, key: int, value):
    # GPS tags are treatedly different
    if not "GPS" in exif_dict:
        exif_dict["GPS"] = {}
    if key in [ # https://exiftool.org/TagNames/GPS.html
        0x001d, # GPSDateStamp
        0x001f, # GPSHPositioningError
    ]:
        exif_dict["GPS"][key] = value
    else:
        raise Exception
    return exif_dict

def add_exif_tag(exif_dict, key: int, value):
    # 34665(0x8769): ExifOffset
    if key in [
        0x0100, # 256(0x0100): width
        0x0101, # 256(0x0101): height
        0x010f, # Make. 生产厂商.
        0x0110, # 272(0x0110): model. device type.
        0x0112, # Orientation
        0x0128, # ResolutionUnit. 1:None, 2:inch, 3:cm
        0x0131, # Software
        0x0132, # ModifyDate
        0x011a, # XResolution
        0x011b, # YResolution
        0x013c, # HostComputer
        0x0213, # YCbCrPositioning
        0x8769, # ExifOffset
        0x8825, # GPSInfo
    ]:
        exif_dict["0th"][key] = value
    elif key in [
        0x9003, # DataTimeOriginal. 精确到秒. 本地时区时间. 并不是utc
        0x9004, # CreateDate. 精确到秒.
        0x9286, # UserComment.
        0x9291, # SubSecTimeOrigina. 毫秒数
        0x9011, # OffsetTimeOriginal. 时区
        0x9208, # LightSource
        0xa420, # ImageUniqueID
    ]:
        exif_dict["Exif"][key] = value
    else:
        raise KeyError
    return exif_dict

def get_exif_dict(file_path_img=None, img_pil: str=None):
    backend = backend.lower()
    if file_path_img is not None:
        assert isinstance(file_path_img, str)
        assert img_pil is None
        img_pil = Im.open(file_path_img)

    if 'exif' in img_pil.info:
        exif_dict = piexif.load(img_pil.info['exif'])
    else:
        exif_dict = get_empty_exif_dict()
    return exif_dict

def save_img_and_exif(img_pil, exif_dict, file_path_save):
    exif_bytes = piexif.dump(exif_dict)
    assert not _utils_file.file_exist(file_path_save)
    img_pil.save(file_path_save, exif=exif_bytes)    
    return file_path_save

def get_exif_tag(exif_dict, key):
    for subdict in exif_dict.values():
        if subdict is None:
            continue
        if key in subdict:
            return subdict[key] 
    return None

def add_exif_to_img(exif_dict, file_path_img, file_path_save=None, check_after_save=False):
    file_path_img = _utils_file.check_file_exist(file_path_img)

    exif_dict_origin = get_exif_dict(file_path_img)
    img = Im.open(file_path_img)
    
    for key, value in exif_dict.items():
        add_exif_tag(exif_dict, key, value)

    if file_path_save is None:
        file_path_save = file_path_img
        _utils_file.delete_file(file_path_img)

    save_img_and_exif(img, exif_dict, file_path_save)
    
    img.close()
    if check_after_save:
        # 验证是否正确加入exif信息
        exif_dict_new = get_exif_dict(file_path_save)
        for key, value in exif_dict_new.items():
            assert get_exif_tag(exif_dict_new, key) == value
    return

def add_device_name_to_exif(file_path_img, device_name, file_path_save, verbose=False):
    file_path_img = _utils_file.check_file_exist(file_path_img)
    import piexif # pip install piexif

    if isinstance(device_name, str):
        device_name_bytes = device_name.encode("utf-8")
    elif isinstance(device_name, bytes):
        device_name_bytes = device_name
    else:
        raise Exception()

    _, suffix = _utils_file.get_file_name_and_suffix(file_path_img)
    suffix = suffix.lower()
    img_pil = Im.open(file_path_img)
    
    if "exif" in img_pil.info:
        exif_dict = piexif.load(img_pil.info['exif'])
        if not "0th" in exif_dict:
            exif_dict["0th"] = {}
    else:
        # 图像文件不包含exif信息.
        exif_dict = get_empty_exif_dict()

    if exif_dict["0th"].get(0x0110) is not None: # overwrite existing value
        # print("Waring. Exif[\"0th\"][0x0110] already has value %s. Overwriting."%(str(exif_dict["0th"][0x0110])))
        pass
    exif_dict["0th"][0x0110] = device_name_bytes # Exif 272: Model
    
    assert not _utils_file.file_exist(file_path_save)
    save_img_and_exif(img_pil, exif_dict, file_path_save)
    assert _utils_file.file_exist(file_path_save)
    img_pil.close()

    if verbose: # 验证exif信息是否已经被正确写入新文件
        assert not _utils_file.file_exist(file_path_save)
        img_pil_new = Im.open(file_path_img)
        exif_dict_new = piexif.load(img_pil_new.info['exif'])
        assert get_exif_tag(exif_dict_new) == device_name_bytes

if __name__=="__main__":
    file_path_img = r"\\192.168.128.4\Data\待处理\←wwf-x17\8f37d6fdd2788a67c93bf6251565a8a3536686343.jpg@!web-comment-note.avif"
    file_path_img = r"\\192.168.128.4\Data\待处理\←wwf-oneplus\WeiXin\mmexport1670321117441.jpg"
    file_path_img = r"\\192.168.128.4\Data\Image\Scan\Scan20240925_18213897.jpg"
    file_path_img = r"\\192.168.128.4\Data\待处理\←icloud\Image20210325_02522300.jpg"
    exif_info = ExifInfo(file_path_img=file_path_img)
    exif_info.print_exif()