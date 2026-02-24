import random


def generate_random_number():
    """Genera un número aleatorio de 4 dígitos sin dígitos repetidos."""
    while True:
        number = str(random.randint(1000, 9999))
        if len(set(number)) == 4:  # Todos los dígitos deben ser diferentes
            return number


def validate_number(number):
    """
    Valida que el número sea válido para el juego.
    - Debe ser una cadena de caracteres
    - Debe tener exactamente 4 dígitos
    - Todos los dígitos deben ser diferentes
    
    Raises:
        ValueError: Si el número no cumple con los requisitos
    
    Returns:
        bool: True si es válido
    """
    if not isinstance(number, str):
        raise ValueError("El numero debe ser una cadena de caracteres")
    if len(number) != 4:
        raise ValueError("El numero debe tener 4 digitos")
    if not number.isdigit():
        raise ValueError("La cadena de numeros debe ser un numero")
    if len(set(number)) != 4:
        raise ValueError("El numero no puede tener digitos repetidos")
    return True


def calculate_fijas_picas(secret_number, guess_number):
    """
    Compara el número secreto con el intento del usuario.
    
    - Fijas: dígitos en la posición correcta
    - Picas: dígitos correctos pero en posición incorrecta
    
    Args:
        secret_number (str): El número secreto de 4 dígitos
        guess_number (str): El intento del usuario
    
    Returns:
        dict: {"fijas": int, "picas": int}
    
    Raises:
        ValueError: Si los números no son válidos
    """
    validate_number(secret_number)
    validate_number(guess_number)
    
    fijas = 0
    picas = 0
    
    # Contar fijas (dígitos en la posición correcta)
    for i in range(4):
        if secret_number[i] == guess_number[i]:
            fijas += 1
    
    # Contar picas (dígitos correctos pero en posición incorrecta)
    for i in range(4):
        if secret_number[i] != guess_number[i]:  # No es fija
            if guess_number[i] in secret_number:
                picas += 1
    
    return {"fijas": fijas, "picas": picas}
 