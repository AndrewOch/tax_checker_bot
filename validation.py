import re


def validate_inn(inn):
    if not inn:
        return False
    if not re.match(r'^\d{10}$', inn):
        return False
    weights = [2, 4, 10, 3, 5, 9, 4, 6, 8, 0]
    check_sum = sum([int(i) * weights[n] for n, i in enumerate(inn[:-1])]) % 11 % 10
    return check_sum == int(inn[-1])
