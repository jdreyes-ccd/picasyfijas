from src.game_functions import validate_number as validate_impl


def validate_number(number):
    """
    Valida que el número sea válido para el juego.
    Retorna True o False en lugar de lanzar excepciones.
    """
    try:
        return validate_impl(number)
    except ValueError:
        return False