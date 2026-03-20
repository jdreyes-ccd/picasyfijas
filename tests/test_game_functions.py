import pytest
from app.numbers import validate_number
from src.game_functions import generate_random_number, validate_number as validate_strict, calculate_fijas_picas


# Tests para validate_number (app/numbers.py - retorna True/False)
def test_digit_only():
    assert validate_number("1234") == True
    assert validate_number("12a3") == False


def test_length_number():
    assert validate_number("1234") == True
    assert validate_number("123") == False
    assert validate_number("12345") == False


def test_unique_digits():
    assert validate_number("1234") == True
    assert validate_number("1123") == False
    assert validate_number("1233") == False


# Tests para validate_number mejorada
def test_validate_number_strict_valid():
    assert validate_strict("1234") == True
    assert validate_strict("5678") == True


def test_validate_number_strict_invalid_length():
    with pytest.raises(ValueError, match="4 digitos"):
        validate_strict("123")
    with pytest.raises(ValueError, match="4 digitos"):
        validate_strict("12345")


def test_validate_number_strict_invalid_chars():
    with pytest.raises(ValueError, match="numero"):
        validate_strict("12a3")


def test_validate_number_strict_invalid_type():
    with pytest.raises(ValueError, match="cadena"):
        validate_strict(1234)


def test_validate_number_strict_repeated_digits():
    with pytest.raises(ValueError, match="repetidos"):
        validate_strict("1123")
    with pytest.raises(ValueError, match="repetidos"):
        validate_strict("1111")


# Tests para generate_random_number
def test_generate_random_number():
    result = generate_random_number()
    assert len(result) == 4
    assert result.isdigit()
    assert len(set(result)) == 4  # Sin dígitos repetidos


# Tests para calculate_fijas_picas
def test_calculate_fijas_picas_all_correct():
    """Prueba cuando el intento es exactamente igual al secreto"""
    result = calculate_fijas_picas("1234", "1234")
    assert result["fijas"] == 4
    assert result["picas"] == 0


def test_calculate_fijas_picas_all_picas():
    """Prueba cuando todos los dígitos son correctos pero en posición incorrecta"""
    result = calculate_fijas_picas("1234", "4321")
    assert result["fijas"] == 0
    assert result["picas"] == 4


def test_calculate_fijas_picas_mixed():
    """Prueba con fijas y picas"""
    result = calculate_fijas_picas("1234", "1324")
    assert result["fijas"] == 2  # 1 en pos 0, 4 en pos 3
    assert result["picas"] == 2  # 3 y 2 en posición incorrecta


def test_calculate_fijas_picas_no_match():
    """Prueba cuando ningún dígito coincide"""
    result = calculate_fijas_picas("1234", "5678")
    assert result["fijas"] == 0
    assert result["picas"] == 0


def test_calculate_fijas_picas_only_fijas():
    """Prueba con solo fijas"""
    result = calculate_fijas_picas("1234", "1256")
    assert result["fijas"] == 2  # 1 en pos 0, 2 en pos 1
    assert result["picas"] == 0


def test_calculate_fijas_picas_invalid_numbers():
    """Prueba que lanza excepción con números inválidos"""
    with pytest.raises(ValueError):
        calculate_fijas_picas("1234", "123")  # Muy corto
    with pytest.raises(ValueError):
        calculate_fijas_picas("1234", "1123")  # Dígitos repetidos


# Tests para Game model con persistencia
def test_game_solo_add_guess():
    """Prueba agregar intento a juego SOLO"""
    from app.models import Game, GameMode
    game = Game(
        mode=GameMode.SOLO,
        player1_name="Test",
        secret_number="1234",
        max_attempts=10
    )
    
    result = game.add_guess("1234", 4, 0)
    assert result["won"] == True
    assert game.attempts_left == 9


def test_game_multiplayer_add_guess_and_turn_change():
    """Prueba cambio de turno en multijugador"""
    from app.models import Game, GameMode
    game = Game(
        mode=GameMode.MULTIPLAYER,
        player1_name="Alice",
        secret_number="1234",
        max_attempts=2
    )
    game.player2_name = "Bob"
    game.secret_number_p2 = "5678"
    
    # Jugador 1 intenta (falla)
    result = game.add_guess_multiplayer(1, "9012", 0, 0)
    assert result["won"] is None
    assert game.current_turn == 2  # Cambió a turno de Jugador 2
    
    # Jugador 2 intenta (falla)
    result = game.add_guess_multiplayer(2, "3456", 0, 0)
    assert result["won"] is None
    assert game.current_turn == 1  # Volvió a turno de Jugador 1


def test_game_multiplayer_draw():
    """Prueba empate cuando ambos agotan intentos"""
    from app.models import Game, GameMode, GameStatus
    game = Game(
        mode=GameMode.MULTIPLAYER,
        player1_name="Alice",
        secret_number="1234",
        max_attempts=2
    )
    game.player2_name = "Bob"
    game.secret_number_p2 = "5678"
    
    # Jugador 1 falla 2 veces
    game.add_guess_multiplayer(1, "9012", 0, 0)
    game.add_guess_multiplayer(1, "3456", 0, 0)
    
    # Jugador 2 falla 2 veces (último intento triggers draw check)
    game.add_guess_multiplayer(2, "1111", 0, 0)
    result = game.add_guess_multiplayer(2, "2222", 0, 0)
    
    assert result["won"] == "draw"
    assert game.winner == "Empate"
    assert game.status == GameStatus.FINISHED