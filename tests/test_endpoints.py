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
    game_manager.clear_all()
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
                # Intento con algunas fijas (usando un número con primeros 2 dígitos correctos)
                # pero diferente para evitar dígitos repetidos
                first_two = secret[:2]
                remaining_digits = [str(d) for d in range(10) if str(d) not in first_two]
                guess = first_two + remaining_digits[0] + remaining_digits[1]
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

    def test_multiplayer_complete_game_flow(self, client):
        """Prueba flujo completo de multijugador con cambio de turnos."""
        # Crear juego (Jugador 1)
        response = client.post("/play/multiplayer", json={"name": "Alice"})
        game_id = response.json()["game_id"]

        # Jugador 2 se une
        response = client.post(
            f"/play/multiplayer/join/{game_id}",
            json={"name": "Bob"}
        )
        assert response.status_code == 200

        # Obtener números secretos
        game = game_manager.get_game(game_id)
        secret_p1 = game.secret_number  # Lo que Bob debe adivinar
        secret_p2 = game.secret_number_p2  # Lo que Alice debe adivinar

        # Turno 1: Jugador 1 intenta
        response = client.post(
            f"/guess/{game_id}/player/1",
            json={"guess": secret_p2}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["won"] == True  # Alice adivinó
        assert data["current_turn"] == 1

    def test_multiplayer_turn_validation(self, client):
        """Prueba que no pueda jugar fuera de su turno."""
        # Crear juego
        response = client.post("/play/multiplayer", json={"name": "Alice"})
        game_id = response.json()["game_id"]

        # Jugador 2 se une
        client.post(
            f"/play/multiplayer/join/{game_id}",
            json={"name": "Bob"}
        )

        # Intentar que Jugador 2 juegue pero es turno de Jugador 1
        response = client.post(
            f"/guess/{game_id}/player/2",
            json={"guess": "1234"}
        )
        assert response.status_code == 400
        assert "No es tu turno" in response.json()["detail"]

    def test_multiplayer_draw(self, client):
        """Prueba que el juego termina en empate cuando ambos agotan intentos."""
        # Crear juego con 2 intentos (como está configurado)
        response = client.post("/play/multiplayer", json={"name": "Alice"})
        game_id = response.json()["game_id"]

        # Jugador 2 se une
        client.post(
            f"/play/multiplayer/join/{game_id}",
            json={"name": "Bob"}
        )

        game = game_manager.get_game(game_id)
        secret_p1 = game.secret_number
        secret_p2 = game.secret_number_p2

        # Alternar turnos: cada jugador falla 2 veces
        # Primero Jugador 1
        wrong1 = "1234" if "1234" != secret_p2 else "5678"
        response = client.post(
            f"/guess/{game_id}/player/1",
            json={"guess": wrong1}
        )
        assert response.status_code == 200
        
        # Luego Jugador 2
        wrong2 = "1234" if "1234" != secret_p1 else "5678"
        response = client.post(
            f"/guess/{game_id}/player/2",
            json={"guess": wrong2}
        )
        assert response.status_code == 200
        
        # Segundo intento Jugador 1
        wrong1_2 = "5678" if "5678" != secret_p2 else "9012"
        response = client.post(
            f"/guess/{game_id}/player/1",
            json={"guess": wrong1_2}
        )
        assert response.status_code == 200
        
        # Segundo intento Jugador 2 - último intento, debe terminar en draw
        wrong2_2 = "5678" if "5678" != secret_p1 else "9012"
        response = client.post(
            f"/guess/{game_id}/player/2",
            json={"guess": wrong2_2}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["won"] == "draw"
        assert "Empate" in data["message"]

    def test_solo_game_persistence(self, client):
        """Prueba que los datos se persisten en PostgreSQL."""
        # Crear juego
        response = client.post("/play/solo", json={"name": "TestUser"})
        game_id = response.json()["game_id"]

        # Hacer un intento
        game = game_manager.get_game(game_id)
        response = client.post(
            f"/guess/{game_id}",
            json={"guess": "1234"}
        )
        assert response.status_code == 200

        # Obtener estado desde servidor (debería venir de PostgreSQL)
        response = client.get(f"/game/{game_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["game_id"] == game_id
        assert len(data["guesses"]) == 1  # El intento está persistido
