import pytest
from pytest_bdd import scenario, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app 

@scenario('features/valid.feature', 'Validate a valid number')
def test_validate_number():
    pass

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def context():
    return {}
    
@given(parsers.parse('I have a number {number}'))
def given_number(context, number):
    context['number'] = number

@when(parsers.parse('I validate the number'))
def when_validate_number(context, client):
    response = client.get(f"/validate/{context['number']}")
    context['response'] = response.json()

@then(parsers.parse('the result should be {result}'))
def then_result(context, result):
    assert str(context['response']['valid']).lower() == result.lower()