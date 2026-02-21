import random

def generate_random_number():
    while True:
        number = str(random.randint(1000, 9999))
        if len(set(number)) > 1:  
            return number

def validate_number(number):
    if not isinstance(number, str):
        raise ValueError ("El numero debe ser una cadena de caracteres")
    if len(number) != 4:
        raise ValueError ("El numero debe tener 4 digitos")
    if not number.isdigit():
        raise ValueError ("La cadena de numeros debe ser un numero")
    return True
    
def compare_numbers(number1, number2):
    if not validate_number(number1) or not validate_number(number2):
        raise ValueError ("No es un numero")
    return number1 == number2
 