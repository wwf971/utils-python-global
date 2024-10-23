
import random

def random_int_in_range(start, end, include_end=False):
    if include_end:
        end += 1
    return random.randrange(start, end)

def multi_random_int_in_range(num, start, end, include_end=False, allow_repeat=False):
    # assert isinstance(num, int)
    if include_end:
        end += 1
    if allow_repeat:
        return random.choices(range(start, end), k=num)
    else:
        return multi_random_int_in_range_no_repeat(num, start, end, include_end)

def multi_random_int_in_range_no_repeat(num, start, end, include_end=False):
    if include_end:
        end += 1
    assert end > start
    assert end - start >= num
    return random.sample(range(start, end), num)

def find_max_element_less_than(target, _list, is_list_sorted=True):
    if not is_list_sorted:
        _list = list(_list).sort()

    # following case is covered, where (None,-1) will be returned
        # len(_list) == 0
        # target <= _list[0]
    left, right = 0, len(_list) - 1
    element = None
    index = -1
    while left <= right:
        mid = (left + right) // 2   
        if _list[mid] < target:
            element = _list[mid]  # found a candidate for B
            left = mid + 1  # look for a larger candidate
            index = mid
        else:
            right = mid - 1  # look for a smaller candidate
    return element, mid

from .sample import (
    sample_from_gaussian_01
)