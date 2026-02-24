from fastapi import FastAPI, Request, HTTPException
from app.numbers import validate_number
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.game_manager import game_manager
from src.game_functions import calculate_fijas_picas, validate_number as validate_strict

app = FastAPI()
template = Jinja2Templates(directory="app/templates")


# Modelos de request
class PlayerName(BaseModel):
    name: str


class GuessRequest(BaseModel):
    guess: str


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return template.TemplateResponse("index.html", {"request": request})


@app.get("/validate/{number}")
def validate_number_endpoint(number: str):
    return {"valid": validate_number(number)}


# ==================== ENDPOINTS DE JUEGO ====================

@app.post("/play/solo")
def create_solo_game(player: PlayerName):
    """
    Crea un nuevo juego solo contra la máquina.
    El jugador tiene 10 intentos para adivinar el número.
    
    Returns:
        - game_id: ID del juego creado
        - message: Mensaje de bienvenida
        - attempts_left: Intentos restantes
    """
    try:
        game = game_manager.create_solo_game(player.name)
        return {
            "game_id": game.game_id,
            "message": f"¡Bienvenido {player.name}! Tienes {game.max_attempts} intentos para adivinar el número.",
            "attempts_left": game.attempts_left,
            "mode": "solo"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/play/multiplayer")
def create_multiplayer_game(player: PlayerName):
    """
    Crea un nuevo juego multijugador.
    El primer jugador crea el juego y espera que otro se una.
    
    Returns:
        - game_id: ID del juego creado
        - message: Mensaje indicando que se espera otro jugador
    """
    try:
        game = game_manager.create_multiplayer_game(player.name)
        return {
            "game_id": game.game_id,
            "message": f"Juego creado por {player.name}. Esperando a otro jugador...",
            "status": "waiting"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/play/multiplayer/join/{game_id}")
def join_multiplayer_game(game_id: str, player: PlayerName):
    """
    Une a un segundo jugador a un juego existente.
    
    Returns:
        - Información del juego actualizado
    """
    try:
        game = game_manager.join_multiplayer_game(player.name, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado o ya en progreso")
        
        return {
            "game_id": game.game_id,
            "message": f"¡{player.name} se ha unido al juego!",
            "player1": game.player1_name,
            "player2": game.player2_name,
            "status": "in_progress"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/guess/{game_id}")
def submit_guess(game_id: str, guess_data: GuessRequest):
    """
    Procesa un intento del jugador.
    Para multijugador con turnos, debes enviar ?player=1 o ?player=2 en la query
    
    Args:
        - game_id: ID del juego
        - guess: El número a adivinar (4 dígitos)
        - player (query param): 1 o 2 (requerido para multijugador)
    
    Returns:
        - fijas: Dígitos en posición correcta
        - picas: Dígitos correctos pero en posición incorrecta
        - attempts_left: Intentos restantes del jugador actual
        - won: True si ganó, False si perdió, None si continúa
        - message: Mensaje descriptivo
        - current_turn: De quién es el siguiente turno (multijugador)
    """
    # Obtener el juego
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    # Validar que el juego esté en progreso
    if game.status.value != "in_progress":
        raise HTTPException(status_code=400, detail=f"El juego ya ha terminado. Ganador: {game.winner}")
    
    # Validar el intento
    try:
        validate_strict(guess_data.guess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Número inválido: {str(e)}")
    
    # MODO SOLO
    if game.mode.value == "solo":
        try:
            result = calculate_fijas_picas(game.secret_number, guess_data.guess)
            fijas = result["fijas"]
            picas = result["picas"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        game_result = game.add_guess(guess_data.guess, fijas, picas)
        
        return {
            "game_id": game.game_id,
            "guess": guess_data.guess,
            "fijas": fijas,
            "picas": picas,
            "attempts_left": game.attempts_left,
            "won": game_result["won"],
            "message": game_result["message"],
            "total_attempts": len(game.guesses),
            "guesses_history": game.guesses
        }
    
    # MODO MULTIJUGADOR (turnos)
    else:
        from fastapi import Query
        # Por simplicidad, el cliente debe indicar de qué jugador es el intento
        # En producción, esto debería venir del usuario autenticado
        raise HTTPException(status_code=400, detail="Para multijugador usa /guess/{game_id}/player/{player_number}")


@app.post("/guess/{game_id}/player/{player_number}")
def submit_guess_multiplayer(game_id: str, player_number: int, guess_data: GuessRequest):
    """
    Procesa un intento en modo MULTIJUGADOR con TURNOS.
    
    Args:
        - game_id: ID del juego
        - player_number: 1 o 2 (cuál jugador está haciendo el intento)
        - guess: El número a adivinar (4 dígitos)
    """
    if player_number not in [1, 2]:
        raise HTTPException(status_code=400, detail="player_number debe ser 1 o 2")
    
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    if game.status.value != "in_progress":
        raise HTTPException(status_code=400, detail=f"El juego ya ha terminado. Ganador: {game.winner}")
    
    # Validar que sea el turno del jugador
    if game.current_turn != player_number:
        other_player = 2 if player_number == 1 else 1
        raise HTTPException(
            status_code=400,
            detail=f"No es tu turno. Es el turno del Jugador {other_player}"
        )
    
    # Validar el intento
    try:
        validate_strict(guess_data.guess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Número inválido: {str(e)}")
    
    # Determinar el número secreto contra el que juega este jugador
    if player_number == 1:
        secret_number = game.secret_number_p2  # P1 intenta adivinar el número de P2
    else:
        secret_number = game.secret_number   # P2 intenta adivinar el número de P1
    
    # Calcular fijas y picas
    try:
        result = calculate_fijas_picas(secret_number, guess_data.guess)
        fijas = result["fijas"]
        picas = result["picas"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Añadir intento con lógica de turnos
    game_result = game.add_guess_multiplayer(player_number, guess_data.guess, fijas, picas)
    
    # Obtener los intentos del jugador actual
    if player_number == 1:
        guesses_history = game.player1_guesses
    else:
        guesses_history = game.player2_guesses
    
    return {
        "game_id": game.game_id,
        "player": player_number,
        "guess": guess_data.guess,
        "fijas": fijas,
        "picas": picas,
        "attempts_left": game_result["attempts_left"],
        "won": game_result["won"],
        "message": game_result["message"],
        "current_turn": game_result["current_turn"],
        "total_attempts": len(guesses_history),
        "guesses_history": guesses_history
    }


@app.get("/game/{game_id}")
def get_game_status(game_id: str):
    """
    Obtiene el estado actual del juego sin revelar el número secreto.
    
    Returns:
        - Información del juego (sin mostrar el número secreto)
    """
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    game_dict = game.to_dict()
    # No revelar el número secreto
    game_dict.pop("secret_number", None)
    return game_dict


@app.get("/games/waiting")
def get_waiting_games():
    """
    Obtiene la lista de juegos multijugador esperando jugadores.
    
    Returns:
        - Lista de juegos en estado WAITING
    """
    return {"waiting_games": game_manager.get_waiting_games()}