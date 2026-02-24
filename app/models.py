from enum import Enum
from typing import Optional
from datetime import datetime
from uuid import uuid4


class GameMode(str, Enum):
    SOLO = "solo"
    MULTIPLAYER = "multiplayer"


class GameStatus(str, Enum):
    WAITING = "waiting"  # Esperando al segundo jugador
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Game:
    def __init__(
        self,
        mode: GameMode,
        player1_name: str,
        secret_number: str,
        max_attempts: int = 10,
        player2_name: Optional[str] = None,
        secret_number_p2: Optional[str] = None,
    ):
        self.game_id = str(uuid4())
        self.mode = mode
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.secret_number = secret_number  # Número secreto del Jugador 1
        self.secret_number_p2 = secret_number_p2  # Número secreto del Jugador 2
        self.max_attempts = max_attempts
        
        # Para modo SOLO
        self.attempts_left = max_attempts
        self.guesses = []
        
        # Para modo MULTIPLAYER (turnos)
        self.player1_attempts_left = max_attempts
        self.player2_attempts_left = max_attempts
        self.player1_guesses = []  # Intentos del P1 adivinando número de P2
        self.player2_guesses = []  # Intentos del P2 adivinando número de P1
        self.current_turn = 1  # Cuyo turno es: 1 o 2
        
        self.status = GameStatus.IN_PROGRESS if mode == GameMode.SOLO else GameStatus.WAITING
        self.winner = None
        self.created_at = datetime.now()
        self.finished_at = None

    def add_guess(self, guess: str, fijas: int, picas: int) -> dict:
        """Añade un intento al juego y retorna el estado actual (MODO SOLO)."""
        self.guesses.append({"guess": guess, "fijas": fijas, "picas": picas})
        self.attempts_left -= 1

        # Verificar si ganó (4 fijas = número correcto)
        if fijas == 4:
            self.status = GameStatus.FINISHED
            self.winner = self.player1_name
            self.finished_at = datetime.now()
            return {
                "won": True,
                "message": f"¡{self.winner} ganó!",
                "fijas": fijas,
                "picas": picas,
                "attempts_left": self.attempts_left,
            }

        # Verificar si perdió (sin intentos restantes)
        if self.attempts_left == 0:
            self.status = GameStatus.FINISHED
            self.winner = "Máquina"
            self.finished_at = datetime.now()
            return {
                "won": False,
                "message": f"Perdiste. El número era {self.secret_number}. {self.winner} ganó.",
                "fijas": fijas,
                "picas": picas,
                "attempts_left": self.attempts_left,
            }

        # Juego continúa
        return {
            "won": None,
            "message": f"Intento registrado. Te quedan {self.attempts_left} intentos.",
            "fijas": fijas,
            "picas": picas,
            "attempts_left": self.attempts_left,
        }

    def add_guess_multiplayer(self, player: int, guess: str, fijas: int, picas: int) -> dict:
        """Añade un intento en modo MULTIJUGADOR con TURNOS."""
        if player == 1:
            self.player1_guesses.append({"guess": guess, "fijas": fijas, "picas": picas})
            self.player1_attempts_left -= 1
            guesses_list = self.player1_guesses
            attempts_left = self.player1_attempts_left
            opponent = self.player2_name
            secret_to_beat = self.secret_number_p2
        else:
            self.player2_guesses.append({"guess": guess, "fijas": fijas, "picas": picas})
            self.player2_attempts_left -= 1
            guesses_list = self.player2_guesses
            attempts_left = self.player2_attempts_left
            opponent = self.player1_name
            secret_to_beat = self.secret_number

        # Verificar si ganó (4 fijas)
        if fijas == 4:
            self.status = GameStatus.FINISHED
            self.winner = self.player1_name if player == 1 else self.player2_name
            self.finished_at = datetime.now()
            return {
                "won": True,
                "message": f"¡{self.winner} ganó adivinando el número de {opponent}!",
                "fijas": fijas,
                "picas": picas,
                "attempts_left": attempts_left,
                "current_turn": self.current_turn,
            }

        # Verificar si perdió (sin intentos)
        if attempts_left == 0:
            self.status = GameStatus.FINISHED
            other_player = 2 if player == 1 else 1
            self.winner = self.player2_name if other_player == 2 else self.player1_name
            self.finished_at = datetime.now()
            return {
                "won": False,
                "message": f"Agotaste tus {self.max_attempts} intentos. El número de {opponent} era {secret_to_beat}. {self.winner} gana.",
                "fijas": fijas,
                "picas": picas,
                "attempts_left": attempts_left,
                "current_turn": self.current_turn,
            }

        # Cambiar de turno
        self.current_turn = 2 if self.current_turn == 1 else 1

        return {
            "won": None,
            "message": f"Intento registrado. Te quedan {attempts_left} intentos. Ahora es turno del {opponent}.",
            "fijas": fijas,
            "picas": picas,
            "attempts_left": attempts_left,
            "current_turn": self.current_turn,
        }

    def to_dict(self) -> dict:
        """Convierte el juego a diccionario para serialización."""
        if self.mode == GameMode.SOLO:
            return {
                "game_id": self.game_id,
                "mode": self.mode.value,
                "status": self.status.value,
                "player1_name": self.player1_name,
                "player2_name": self.player2_name,
                "attempts_left": self.attempts_left,
                "guesses": self.guesses,
                "winner": self.winner,
                "created_at": self.created_at.isoformat(),
            }
        else:  # MULTIPLAYER
            return {
                "game_id": self.game_id,
                "mode": self.mode.value,
                "status": self.status.value,
                "player1_name": self.player1_name,
                "player2_name": self.player2_name,
                "player1_attempts_left": self.player1_attempts_left,
                "player2_attempts_left": self.player2_attempts_left,
                "player1_guesses": self.player1_guesses,
                "player2_guesses": self.player2_guesses,
                "current_turn": self.current_turn,
                "winner": self.winner,
                "created_at": self.created_at.isoformat(),
            }
