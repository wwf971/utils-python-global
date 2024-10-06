import string, random, re

def get_alphabet_az_AZ():
    return string.ascii_letters

def get_alphabet_az():
    return string.ascii_lowercase

def get_alphabet_AZ():
    return string.ascii_uppercase

def get_alphabet_09():
    return string.digits

def get_random_str_az_AZ_09(length):
    alphabet = get_alphabet_az_AZ() + get_alphabet_09()
    return get_random_str(length, alphabet=alphabet)

def get_random_str_az_AZ(length):
    alphabet = string.ascii_letters  # Use letters from 'a-z', 'A-Z'
    return get_random_str(length, alphabet=alphabet)

def get_random_str(length, alphabet:list):
    return ''.join(random.choice(alphabet) for _ in range(length))

def binary_string_to_int(string_binary: str, large_side:str="left", BigEndian=False):
    # large_side: most significant bit.
        # large_side == "left" : big endian
            # "0b1001" --> 9
            # "011001" --> 25
        # large_side == "right": small endian
    string_binary = string_binary.lower()

    result = re.match(r"0b(.*)", string_binary)
    if result is not None:
        string_binary = result.group(1)

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
    for i in index_list:
        if string_binary[i] == "0":
            pass
        elif string_binary[i] == "1":
            int_value += int_base
        else:
            raise ValueError
        int_base *= 2
    return int_value

def int_to_binary_string(int_value, digit_num: int=None, prefix: str=None):
    pattern = []
    # if _0bPrefix:
    #     Pattern.append("#")
    if digit_num is not None:
        assert isinstance(digit_num, int)
        pattern.append("0")
        pattern.append(str(digit_num))
    
    pattern.append("b")
    pattern_str = "".join(pattern)

    binary_string = format(int_value, pattern_str)
        # format(14, '#010b') => '0b00001110'
        # format(14, '010b') => '0000001110'
            # b: binary.
            # 010: add leading zeros to make (at least) 10 digits in total
    
    if prefix is not None:
        binary_string = prefix + binary_string
    return binary_string
