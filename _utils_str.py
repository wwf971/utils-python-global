import string, random, re

def get_alphabet_az():
    return string.ascii_lowercase

def get_alphabet_AZ():
    return string.ascii_uppercase

def get_alphabet_az_AZ():
    return string.ascii_letters

def get_alphabet_09():
    return string.digits

def get_alphabet_az_AZ_09():
    return get_alphabet_az_AZ() + get_alphabet_09()

def get_random_str_az_AZ_09(length):
    alphabet = get_alphabet_az_AZ() + get_alphabet_09()
    return get_random_str(length, alphabet=alphabet)

def get_random_str_az_AZ(length):
    alphabet = string.ascii_letters  # Use letters from 'a-z', 'A-Z'
    return get_random_str(length, alphabet=alphabet)

def get_random_str_AZ_09(length):
    alphabet = get_alphabet_AZ() + get_alphabet_09()
    return get_random_str(length, alphabet=alphabet)

def get_random_str(length, alphabet:list=None):
    if alphabet is None:
        alphabet = get_alphabet_az_AZ_09()
    return ''.join(random.choice(alphabet) for _ in range(length))

def str_01_to_int(string_binary: str, large_side:str="left", big_endian=False):
    # large_side: most significant bit.
        # large_side == "left" : big endian
            # "0b1001" --> 9
            # "011001" --> 25
        # large_side == "right": small endian
    string_binary = string_binary.lower()

    result = re.match(r"(0b)?(.*)", string_binary)
    if result is not None:
        string_binary = result.group(2)

    for bit in string_binary:
        assert bit == "0" or bit == "1"
    
    large_side = large_side.lower()
    if large_side in ["left", "l", "natural"]:
        index_list = range(len(string_binary))
    elif large_side in ["right", "r"]:
        index_list = reversed(range(len(string_binary)))
    else:
        raise ValueError(large_side)

    int_value = 0
    int_base = 1
    for i in index_list:
        if string_binary[i] == "0":
            pass
        elif string_binary[i] == "1":
            int_value += int_base
        else:
            raise ValueError
        int_base *= 2
    return int_value

def int_to_str_01(int_value, digit_num: int=None, prefix: str=None):
    pattern = []
    # if _0bPrefix:
    #     Pattern.append("#")
    if digit_num is not None:
        assert isinstance(digit_num, int)
        pattern.append("0")
        pattern.append(str(digit_num))
    
    pattern.append("b")
    pattern_str = "".join(pattern)

    str_01 = format(int_value, pattern_str)
        # format(14, '#010b') => '0b00001110'
        # format(14, '010b') => '0000001110'
            # b: binary.
            # 010: add leading zeros to make (at least) 10 digits in total

    if prefix is not None:
        str_01 = prefix + str_01
    return str_01
int_to_binary_str = int_to_str_01

def str_01_to_bytes(_str):
    try:
        _int = int(_str[::-1], 2)
        # why [::-1]?
        # # int('1010', 2) --> 10, not 5
    except Exception:
        return
    _bytes = _int.to_bytes(8, 'little')
    return _bytes

def bytes_to_str_01(_bytes: bytes, reverse=False, space_every=None) -> str:
    if space_every:
        if reverse:
            _bytes = _bytes[::-1]
        i = 0
        str_list = []
        for byte in _bytes:
            if reverse: # bytes are reversed by default. byte: 233(0b1110 1001) --> {byte:08b} is '1110 1101'
                str_list.append(f'{byte:08b}')
            else:
                str_list.append(f'{byte:08b}'[::-1])
            i += 1
            if i % space_every == 0 and i < len(_bytes):
                str_list.append(' ')
        return ''.join(str_list)
    else:
        return ''.join(f'{byte:08b}' if reverse else f'{byte:08b}'[::-1] for byte in (_bytes[::-1] if reverse else _bytes))

def increase_indent(_str:str, indent="    "):
    lines = _str.split("\n")
    lines_indent = [indent + line if len(line) > 0 else line for line in lines]
    return "\n".join(lines_indent)

def is_only_whitespace(s):
    return s == '' or s.isspace()

def is_only_whitespace_test():
    print(is_only_whitespace("   \t\n\r"))   # True
    print(is_only_whitespace(""))            # True or False, depending on your needs
    print(is_only_whitespace("text"))        # False

def is_empty_line(line: str): # no visible characters
    return line.isspace() or line == ''

def remove_empty_line(_str: str):
    _str = _str.replace("\r\n", '\n')
        # on windows system, line break is \r\n
    lines = _str.split('\n')

    lines_new = []
    for line in lines:
        if is_empty_line(line): # this line only has spaces
            # leading_space_num_list.append(None)
            continue
        else:
            lines_new.append(line)

    return "\n".join(lines_new)

def remove_extra_whitespace(_str: str):
    _str = _str.replace("\r\n", '\n')
        # win: line break is \r\n
        # macos/linux: line break is \n
    lines = _str.split('\n')
    line_num = len(lines)
    leading_space_num_list = []
    for index, line in enumerate(lines):
        if line.isspace() or line == '': # this line only has spaces
            # leading_space_num_list.append(None)
            continue
        else:
            leading_space_num = 0
            for char in line:
                if char == ' ':
                    leading_space_num += 1
                else:
                    break
            leading_space_num_list.append(leading_space_num)

    leading_space_num_min = min(leading_space_num_list)
    
    lines_new = []
    for index, line in enumerate(lines):
        if is_empty_line(line):
            lines_new.append('')
        else:
            lines_new.append(line[leading_space_num_min:])
    _str_new = '\n'.join(lines_new)
    _str_new = _str_new.lstrip('\n')
    _str_new = _str_new.rstrip('\n')
    return _str_new


def split_by_group(_str, re_match_result):
    group_spans = {i: re_match_result.span(i) for i in range(1, len(re_match_result.groups()) + 1)}
    slices = []
    group_slice_index = {} # to find slice index of group i --> group_slice_index[i]

    last_index = 0
    sorted_spans = sorted(group_spans.items(), key=lambda x: x[1][0])

    for group_index, (start, end) in sorted_spans:
        if last_index < start:
            slices.append(_str[last_index:start])  # non-group part
        slices.append(_str[start:end])              # group part
        group_slice_index[group_index] = len(slices) - 1
        last_index = end

    if last_index < len(_str):
        slices.append(_str[last_index:])  # trailing non-group part

    return slices, group_slice_index