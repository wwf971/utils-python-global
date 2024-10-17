
import re

B = 1
KB = 1024
MB = 1048576
GB = 1073741824
TB = 1099511627776

def num_to_str_1024(num: int):
    if num < KB:
        str_1024 = "%d"%num
    elif num < MB:
        str_1024 = "%.3f K"%(1.0 * num / KB)
    elif num < GB:
        str_1024 = "%.3f M"%(1.0 * num / MB)
    elif num < TB:
        str_1024 = "%.3f G"%(1.0 * num / GB)
    else:
        str_1024 = "%.3f T"%(1.0 * num / TB)
    return str_1024

def size_str_to_byte_num(size_str: str):
    Pattern = r"(.*)([Byte|B|k|K|kb|kB|KB|MB|MiB|mb|m|g|gb|GB|])"
    result = re.match(Pattern, size_str)
    if result is None:
        raise Exception
    unit_num_str = result.group(1)
    unit_str = result.group(2)
    unit_num = int(unit_num_str)

    unit_str = unit_str.lower()
    if unit_str in ["b", "byte"]:
        unit_byte_num = B
    elif unit_str in ["k", "kb"]:
        unit_byte_num = KB
    elif unit_num in ["m", "mb", "mib"]:
        unit_byte_num = MB
    elif unit_num in ["g", "gb", "gyga", "gygabyte"]:
        unit_byte_num = GB
    else:
        raise Exception()
    return unit_num * unit_byte_num

def byte_num_to_size_str(byte_num):
    if byte_num < KB:
        Str = "%d B"%byte_num
    elif byte_num < MB:
        Str = "%.3f KB"%(1.0 * byte_num / KB)
    elif byte_num < GB:
        Str = "%.3f MB"%(1.0 * byte_num / MB)
    elif byte_num < TB:
        Str = "%.3f GB"%(1.0 * byte_num / GB)
    else:
        Str = "%.3f TB"%(1.0 * byte_num / TB)
    return Str