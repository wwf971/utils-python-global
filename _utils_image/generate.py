from _utils_import import np

def get_black_image_np_int255(height=512, width=512, channel_num=3):
    assert 1<= channel_num <= 4
    return np.ones(shape=(height, width, channel_num), dtype=np.uint8)

