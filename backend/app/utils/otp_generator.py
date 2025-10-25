import random
import string

def generate_otp(length=6, allow_letter=True):
    digits = list('0123456789')
    if allow_letter:
        char_set = digits + list(string.ascii_uppercase)
    else:
        char_set = digits
    return ''.join(random.choices(char_set, k=length))
