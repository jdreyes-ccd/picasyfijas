import pytest
from fastapi.testclient import TestClient
from pytest_bdd import scenario, given, when, then, parsers

from app.main import app
from app.game_manager import game_manager


@scenario("features/solo_service.feature", "Create a solo game")
def test_bdd_create_solo_game():
    """Scenario wrapper required by pytest-bdd; step implementations are defined below."""
    return None


@scenario("features/solo_service.feature", "Reject invalid guess in solo game")
def test_bdd_reject_invalid_solo_guess():
    """Scenario wrapper required by pytest-bdd; step implementations are defined below."""
    return None
    


@scenario("features/solo_service.feature", "Get solo game status")
def test_bdd_get_solo_game_status():
    """Scenario wrapper required by pytest-bdd; step implementations are defined below."""
    return None


@scenario("features/multiplayer_service.feature", "Create multiplayer game in waiting state")
def test_bdd_create_multiplayer_waiting():
    """Scenario wrapper required by pytest-bdd; step implementations are defined below."""
    return None


@scenario("features/multiplayer_service.feature", "Join multiplayer game")
def test_bdd_join_multiplayer_game():
    """Scenario wrapper required by pytest-bdd; step implementations are defined below."""
    return None


@scenario("features/multiplayer_service.feature", "Reject guess out of turn in multiplayer")
def test_bdd_reject_guess_out_of_turn():
    """Scenario wrapper required by pytest-bdd; step implementations are defined below."""
    return None


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def context():
    return {}


@pytest.fixture(autouse=True)
def clear_games():
    game_manager.clear_all()
    yield


@given(parsers.parse('I am a player named "{name}"'))
def given_player_name(context, name):
    context["player_name"] = name


@when("I start a solo game")
def when_start_solo_game(context, client):
    response = client.post("/play/solo", json={"name": context["player_name"]})
    context["response"] = response
    if response.status_code == 200:
        context["data"] = response.json()
        context["game_id"] = context["data"]["game_id"]


@then("the solo game should be created with 10 attempts")
def then_solo_game_created(context):
    response = context["response"]
    data = response.json()
    assert response.status_code == 200
    assert "game_id" in data
    assert data["attempts_left"] == 10
    assert data["mode"] == "solo"


@given(parsers.parse('I started a solo game for "{name}"'))
def given_started_solo_game(context, client, name):
    response = client.post("/play/solo", json={"name": name})
    assert response.status_code == 200
    data = response.json()
    context["game_id"] = data["game_id"]


@when(parsers.parse('I submit guess "{guess}" in that solo game'))
def when_submit_solo_guess(context, client, guess):
    response = client.post(f"/guess/{context['game_id']}", json={"guess": guess})
    context["response"] = response


@when("I request the current game status")
def when_request_game_status(context, client):
    response = client.get(f"/game/{context['game_id']}")
    context["response"] = response
    if response.status_code == 200:
        context["data"] = response.json()


@then("the game status response should include the same game id")
def then_game_status_has_same_id(context):
    response = context["response"]
    data = context["data"]
    assert response.status_code == 200
    assert data["game_id"] == context["game_id"]


@given(parsers.parse('player "{player}" creates a multiplayer game'))
def given_player_creates_multiplayer(context, client, player):
    response = client.post("/play/multiplayer", json={"name": player})
    context["response"] = response
    if response.status_code == 200:
        context["data"] = response.json()
        context["game_id"] = context["data"]["game_id"]


@then("the multiplayer game should be in waiting status")
def then_multiplayer_waiting(context):
    response = context["response"]
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "waiting"


@given(parsers.parse('player "{player}" has a waiting multiplayer game'))
def given_player_has_waiting_game(context, client, player):
    response = client.post("/play/multiplayer", json={"name": player})
    assert response.status_code == 200
    data = response.json()
    context["game_id"] = data["game_id"]


@when(parsers.parse('player "{player}" joins that multiplayer game'))
def when_player_joins_multiplayer(context, client, player):
    response = client.post(
        f"/play/multiplayer/join/{context['game_id']}",
        json={"name": player},
    )
    context["response"] = response
    if response.status_code == 200:
        context["data"] = response.json()


@then("the multiplayer game should be in progress")
def then_multiplayer_in_progress(context):
    response = context["response"]
    data = context["data"]
    assert response.status_code == 200
    assert data["status"] == "in_progress"


@given(parsers.parse('players "{player1}" and "{player2}" are in a multiplayer game'))
def given_players_in_multiplayer_game(context, client, player1, player2):
    create_response = client.post("/play/multiplayer", json={"name": player1})
    assert create_response.status_code == 200
    game_id = create_response.json()["game_id"]

    join_response = client.post(f"/play/multiplayer/join/{game_id}", json={"name": player2})
    assert join_response.status_code == 200

    context["game_id"] = game_id


@when(parsers.cfparse('player {player_number:d} submits guess "{guess}" in multiplayer game'))
def when_player_submits_multiplayer_guess(context, client, player_number, guess):
    response = client.post(
        f"/guess/{context['game_id']}/player/{player_number}",
        json={"guess": guess},
    )
    context["response"] = response
    context["data"] = response.json()


@then(parsers.cfparse("the response status should be {status_code:d}"))
def then_response_status(context, status_code):
    assert context["response"].status_code == status_code


@then(parsers.parse('the response detail should contain "{message}"'))
def then_response_detail_contains(context, message):
    data = context["data"]
    assert "detail" in data
    assert message in data["detail"]
