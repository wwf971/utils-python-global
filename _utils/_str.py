import string, random

def get_alphabet_az_AZ():
    return string.ascii_letters

def get_alphabet_az():
    return string.ascii_lowercase

def get_alphabet_AZ():
    return string.ascii_uppercase

def get_alphabet_digit():
    return string.digits

def get_random_string_az_AZ(length):
    alphabet = string.ascii_letters  # Use letters from 'a-z', 'A-Z'
    return get_random_string(length, alphabet=alphabet)

def get_random_string(length, alphabet:list):
    return ''.join(random.choice(alphabet) for _ in range(length))