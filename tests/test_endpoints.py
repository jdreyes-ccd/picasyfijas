import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.game_manager import game_manager


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_games():
    """Limpia los juegos antes de cada test."""
    game_manager.games.clear()
    game_manager.waiting_players.clear()
    yield


class TestSoloGame:
    def test_create_solo_game(self, client):
        """Prueba crear un juego solo."""
        response = client.post(
            "/play/solo",
            json={"name": "Juan"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert data["mode"] == "solo"
        assert data["attempts_left"] == 10
        assert "Juan" in data["message"]

    def test_solo_game_guess_valid(self, client):
        """Prueba hacer un intento en juego solo."""
        # Crear juego
        response = client.post("/play/solo", json={"name": "Juan"})
        game_id = response.json()["game_id"]

        # Obtener el número secreto del juego
        game = game_manager.get_game(game_id)
        secret = game.secret_number

        # Primer intento correcto
        response = client.post(
            f"/guess/{game_id}",
            json={"guess": secret}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["fijas"] == 4
        assert data["picas"] == 0
        assert data["won"] == True
        assert data["attempts_left"] == 9

    def test_solo_game_guess_invalid_format(self, client):
        """Prueba enviar un número inválido."""
        response = client.post("/play/solo", json={"name": "Juan"})
        game_id = response.json()["game_id"]

        # Número inválido (solo 3 dígitos)
        response = client.post(
            f"/guess/{game_id}",
            json={"guess": "123"}
        )
        assert response.status_code == 400

    def test_solo_game_lose_after_10_attempts(self, client):
        """Prueba perder tras 10 intentos fallidos."""
        response = client.post("/play/solo", json={"name": "Juan"})
        game_id = response.json()["game_id"]
        game = game_manager.get_game(game_id)
        secret = game.secret_number

        # Hacer 10 intentos fallidos
        wrong_numbers = [
            "1234", "5678", "9012", "3456", "7890",
            "2345", "4567", "6789", "0123", "1357"
        ]

        for i, wrong_number in enumerate(wrong_numbers):
            # Asegurar que no es el número secreto
            if wrong_number == secret:
                wrong_number = "9876"

            response = client.post(
                f"/guess/{game_id}",
                json={"guess": wrong_number}
            )

            if i < 9:
                assert response.status_code == 200
                assert response.json()["won"] is None
            else:
                # Último intento
                assert response.status_code == 200
                data = response.json()
                assert data["won"] == False
                assert data["attempts_left"] == 0


class TestMultiplayerGame:
    def test_create_multiplayer_game(self, client):
        """Prueba crear juego multijugador."""
        response = client.post(
            "/play/multiplayer",
            json={"name": "Alice"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert data["status"] == "waiting"
        assert "Alice" in data["message"]

    def test_join_multiplayer_game(self, client):
        """Prueba que segundo jugador se una."""
        # Crear juego
        response = client.post("/play/multiplayer", json={"name": "Alice"})
        game_id = response.json()["game_id"]

        # Segundo jugador se une
        response = client.post(
            f"/play/multiplayer/join/{game_id}",
            json={"name": "Bob"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["player1"] == "Alice"
        assert data["player2"] == "Bob"

    def test_join_nonexistent_game(self, client):
        """Prueba unirse a juego inexistente."""
        response = client.post(
            "/play/multiplayer/join/nonexistent",
            json={"name": "Bob"}
        )
        assert response.status_code == 404

    def test_get_waiting_games(self, client):
        """Prueba obtener lista de juegos esperando."""
        # Crear dos juegos
        client.post("/play/multiplayer", json={"name": "Alice"})
        client.post("/play/multiplayer", json={"name": "Charlie"})

        response = client.get("/games/waiting")
        assert response.status_code == 200
        data = response.json()
        assert len(data["waiting_games"]) == 2


class TestGameStatus:
    def test_get_game_status(self, client):
        """Prueba obtener estado del juego sin revelar número."""
        response = client.post("/play/solo", json={"name": "Juan"})
        game_id = response.json()["game_id"]

        response = client.get(f"/game/{game_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["game_id"] == game_id
        assert "secret_number" not in data  # No revelar el secreto

    def test_get_nonexistent_game(self, client):
        """Prueba obtener juego inexistente."""
        response = client.get("/game/nonexistent")
        assert response.status_code == 404


class TestGameFlow:
    def test_complete_solo_game_flow(self, client):
        """Prueba flujo completo de un juego solo."""
        # Crear juego
        response = client.post("/play/solo", json={"name": "Juan"})
        assert response.status_code == 200
        game_id = response.json()["game_id"]

        # Obtener el número secreto
        game = game_manager.get_game(game_id)
        secret = game.secret_number

        # Hacer intentos hasta ganar
        attempts = 0
        max_attempts = 10

        while attempts < max_attempts:
            if attempts == 0:
                # Intento completamente incorrecto
                guess = "1234" if "1234" != secret else "5678"
            elif attempts == 1:
                # Intento con algunas fijas
                guess = secret[:2] + "99"
            else:
                # Intento correcto
                guess = secret

            response = client.post(
                f"/guess/{game_id}",
                json={"guess": guess}
            )

            assert response.status_code == 200
            data = response.json()

            if guess == secret:
                assert data["won"] == True
                break
            else:
                assert data["won"] is None

            attempts += 1

        assert attempts < max_attempts  # Debe ganar antes de agotar intentos
