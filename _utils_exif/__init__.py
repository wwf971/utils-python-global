
# pip install exifread
# pip install piexif

import _utils_exif.piexif as _utils_exif_piexif
import _utils_exif.pil as pil

def get_exif(img_file_path, backend="piexif", verbose=False):
    backend = backend.lower()
    if backend in ["exifread"]:
        return get_exif_exifread(img_file_path, verbose=verbose)
    elif backend in ["pil", "PIL"]:
        return pil.get_exif(img_file_path, verbose)
    elif backend in ["piexif"]:
        return _utils_exif_piexif.get_exif(img_file_path)
    else:
        raise ValueError

def get_exif_exifread(img_file_path, verbose=False):
    # ref: blog.csdn.net/lmj2006/article/details/136991546
    import exifread # pip install exifread
    exif_dict = {}
    with open(img_file_path, 'rb') as img_file:
        tags = exifread.process_file(img_file)
        sorted_keys = sorted(tags)
        for tag in sorted_keys:
            if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename'):
                if verbose:
                    print(f"{tag}: {tags[tag]}")
                exif_dict[tag] = tags[tag]
    return exif_dict

def unit_test():
    exif_dict = ImagePIL.getexif()
    import pyexiv2
        # pip3 install py3exiv2
        # × pip install pyexiv2

    metadata = pyexiv2.ImageMetadata(file_path_img)
    metadata.read()
    # userdata={'Category':'Human',
    #         'Physical': {
    #             'skin_type':'smooth',
    #             'complexion':'fair'
    #             },
    #         'Location': {
    #             'city': 'london'
    #             }
    #         }
    # metadata['Exif.Photo.UserComment']=json.dumps(userdata)
    metadata.write()

    # altitude = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
    # print(altitude)
    import rasterio
        # pip install rasterio
    TargetDirPath = DLUtils.file.StandardizeDirPath(TargetDirPath)
    old_file=rasterio.open(
        TargetDirPath + "Screen2022122_1245700.png"
    )
    profile=old_file.profile
    data=old_file.read()
    with rasterio.open('new_image.tif','w',**profile) as dst:
        dst.update_tags(a='1', b='2')
        dst.write(data)
        dst.close()