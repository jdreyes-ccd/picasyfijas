from typing import Optional, Dict
from app.models import Game, GameMode, GameStatus
from src.game_functions import generate_random_number
from app.database import SessionLocal, init_db
from app.db_models import GameRecord


class GameManager:
    """Gestor de sesiones de juego con persistencia en base de datos."""

    def __init__(self):
        self.games: Dict[str, Game] = {}
        self.waiting_players: Dict[str, str] = {}  # {player_name: game_id}
        init_db()

    def _upsert_game(self, game: Game) -> None:
        with SessionLocal() as db:
            record = db.get(GameRecord, game.game_id)
            if not record:
                record = GameRecord(game_id=game.game_id)
                db.add(record)

            record.mode = game.mode.value
            record.status = game.status.value
            record.player1_name = game.player1_name
            record.player2_name = game.player2_name
            record.secret_number = game.secret_number
            record.secret_number_p2 = game.secret_number_p2
            record.max_attempts = game.max_attempts
            record.attempts_left = game.attempts_left
            record.guesses = game.guesses
            record.player1_attempts_left = game.player1_attempts_left
            record.player2_attempts_left = game.player2_attempts_left
            record.player1_guesses = game.player1_guesses
            record.player2_guesses = game.player2_guesses
            record.current_turn = game.current_turn
            record.winner = game.winner
            record.created_at = game.created_at
            record.finished_at = game.finished_at
            db.commit()

    def _build_game_from_record(self, record: GameRecord) -> Game:
        game = Game(
            mode=GameMode(record.mode),
            player1_name=record.player1_name,
            secret_number=record.secret_number,
            max_attempts=record.max_attempts,
            player2_name=record.player2_name,
            secret_number_p2=record.secret_number_p2,
        )
        game.game_id = record.game_id
        game.status = GameStatus(record.status)
        game.attempts_left = record.attempts_left
        game.guesses = record.guesses or []
        game.player1_attempts_left = record.player1_attempts_left
        game.player2_attempts_left = record.player2_attempts_left
        game.player1_guesses = record.player1_guesses or []
        game.player2_guesses = record.player2_guesses or []
        game.current_turn = record.current_turn
        game.winner = record.winner
        game.created_at = record.created_at
        game.finished_at = record.finished_at
        return game

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
        self._upsert_game(game)
        return game

    def create_multiplayer_game(self, player1_name: str) -> Game:
        """Crea un juego de multijugador esperando al segundo jugador."""
        secret_number = generate_random_number()
        game = Game(
            mode=GameMode.MULTIPLAYER,
            player1_name=player1_name,
            secret_number=secret_number,
            max_attempts=2,
        )
        self.games[game.game_id] = game
        self.waiting_players[player1_name] = game.game_id
        self._upsert_game(game)
        return game

    def join_multiplayer_game(self, player2_name: str, game_id: str) -> Optional[Game]:
        """Une un segundo jugador a un juego existente."""
        game = self.get_game(game_id)
        if not game:
            return None
        
        # Verificar que esté en estado WAITING y sea multijugador
        if game.status.value != "waiting" or game.mode != GameMode.MULTIPLAYER:
            return None

        game.player2_name = player2_name
        # Generar número secreto para el Jugador 2

        game.secret_number_p2 = generate_random_number()
        game.status = GameStatus.IN_PROGRESS
        
        # Remover del pool de jugadores esperando sin copiar el diccionario.
        player_to_remove = next(
            (player for player, gid in self.waiting_players.items() if gid == game_id),
            None,
        )
        if player_to_remove is not None:
            del self.waiting_players[player_to_remove]

    
        self.games[game.game_id] = game
        self._upsert_game(game)

        return game


    def get_game(self, game_id: str) -> Optional[Game]:
        """Obtiene un juego por ID."""
        cached = self.games.get(game_id)
        if cached:
            return cached

        with SessionLocal() as db:
            record = db.get(GameRecord, game_id)
            if not record:
                return None
            game = self._build_game_from_record(record)
            self.games[game_id] = game
            return game

    def save_game(self, game: Game) -> None:
        """Guarda los cambios de una partida en memoria y DB."""
        self.games[game.game_id] = game
        self._upsert_game(game)

    def delete_game(self, game_id: str) -> bool:
        """Elimina un juego (limpieza)."""
        deleted = False
        if game_id in self.games:
            del self.games[game_id]
            deleted = True

        with SessionLocal() as db:
            record = db.get(GameRecord, game_id)
            if record:
                db.delete(record)
                db.commit()
                deleted = True

        return deleted

    def clear_all(self) -> None:
        """Limpia memoria y base de datos (uso de pruebas)."""
        self.games.clear()
        self.waiting_players.clear()
        with SessionLocal() as db:
            db.query(GameRecord).delete()
            db.commit()

    def get_waiting_games(self) -> list:
        """Retorna lista de juegos esperando jugadores."""
        with SessionLocal() as db:
            waiting_records = db.query(GameRecord).filter(GameRecord.status == GameStatus.WAITING.value).all()

        waiting_games = []
        for record in waiting_records:
            game = self._build_game_from_record(record)
            self.games[game.game_id] = game
            waiting_games.append(game.to_dict())

        return waiting_games


# Instancia global del gestor
game_manager = GameManager()
