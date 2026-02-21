def validate_number(number):
    if len(number) != 4:
        return False
    if not number.isdigit():
        return False
    for i in range(4):
        for j in range(i + 1, 4):
            if number[i] == number[j]:
                return False
    return True