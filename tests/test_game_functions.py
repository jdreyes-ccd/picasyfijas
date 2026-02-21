import pytest
from app.numbers import validate_number

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

'''
from src.game_functions import generate_random_number, validate_number, compare_numbers

def test_generate_random_number():
    result = generate_random_number()
    assert len(result) == 4

def test_validate_number():
    with pytest.raises(ValueError):
       validate_number("123")

def test_compare_numbers():
    with pytest.raises(ValueError):
        compare_numbers("124", "1234")

'''