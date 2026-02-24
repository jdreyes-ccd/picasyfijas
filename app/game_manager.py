from typing import Optional, Dict
from app.models import Game, GameMode, GameStatus
from src.game_functions import generate_random_number


class GameManager:
    """Gestor de sesiones de juego en memoria."""

    def __init__(self):
        self.games: Dict[str, Game] = {}
        self.waiting_players: Dict[str, str] = {}  # {player_name: game_id}

    def create_solo_game(self, player_name: str) -> Game:
        """Crea un juego nuevo contra la máquina."""
        secret_number = generate_random_number()
        game = Game(
            mode=GameMode.SOLO,
            player1_name=player_name,
            secret_number=secret_number,
            max_attempts=10,
        )
        self.games[game.game_id] = game
        return game

    def create_multiplayer_game(self, player1_name: str) -> Game:
        """Crea un juego de multijugador esperando al segundo jugador."""
        secret_number = generate_random_number()
        game = Game(
            mode=GameMode.MULTIPLAYER,
            player1_name=player1_name,
            secret_number=secret_number,
            max_attempts=10,
        )
        self.games[game.game_id] = game
        self.waiting_players[player1_name] = game.game_id
        return game

    def join_multiplayer_game(self, player2_name: str, game_id: str) -> Optional[Game]:
        """Une un segundo jugador a un juego existente."""
        if game_id not in self.games:
            return None

        game = self.games[game_id]
        
        # Verificar que esté en estado WAITING y sea multijugador
        if game.status.value != "waiting" or game.mode != GameMode.MULTIPLAYER:
            return None

        game.player2_name = player2_name
        # Generar número secreto para el Jugador 2
        game.secret_number_p2 = generate_random_number()
        game.status = GameStatus.IN_PROGRESS
        
        # Remover del pool de jugadores esperando
        for player, gid in list(self.waiting_players.items()):
            if gid == game_id:
                del self.waiting_players[player]
                break

        return game

    def get_game(self, game_id: str) -> Optional[Game]:
        """Obtiene un juego por ID."""
        return self.games.get(game_id)

    def delete_game(self, game_id: str) -> bool:
        """Elimina un juego (limpieza)."""
        if game_id in self.games:
            del self.games[game_id]
            return True
        return False

    def get_waiting_games(self) -> list:
        """Retorna lista de juegos esperando jugadores."""
        return [
            game.to_dict()
            for game in self.games.values()
            if game.status.value == "waiting"
        ]


# Instancia global del gestor
game_manager = GameManager()
