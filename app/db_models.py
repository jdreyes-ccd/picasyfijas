from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.types import JSON

from app.database import Base


class GameRecord(Base):
    __tablename__ = "games"

    game_id = Column(String(64), primary_key=True, index=True)
    mode = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    player1_name = Column(String(120), nullable=False)
    player2_name = Column(String(120), nullable=True)
    secret_number = Column(String(4), nullable=False)
    secret_number_p2 = Column(String(4), nullable=True)
    max_attempts = Column(Integer, nullable=False)

    attempts_left = Column(Integer, nullable=False)
    guesses = Column(JSON, nullable=False)

    player1_attempts_left = Column(Integer, nullable=False)
    player2_attempts_left = Column(Integer, nullable=False)
    player1_guesses = Column(JSON, nullable=False)
    player2_guesses = Column(JSON, nullable=False)
    current_turn = Column(Integer, nullable=False)

    winner = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
