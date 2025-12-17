from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class GamePhase(Enum):
    LOBBY = "lobby"
    ROUND_1 = "round_1"
    ROUND_2 = "round_2"
    GAME_OVER = "game_over"

class QuestionState(Enum):
    BOARD_ACTIVE = "board_active"
    QUESTION_REVEALED = "question_revealed"
    BUZZING_OPEN = "buzzing_open"
    ANSWER_IN_PROGRESS = "answer_in_progress"

@dataclass
class Player:
    id: str
    name: str
    team_id: str
    session_id: str
    connected: bool = True

@dataclass
class Team:
    id: str
    name: str
    score: int = 0
    player_ids: List[str] = field(default_factory=list)
    color: str = "#FFD700"  # Gold default

@dataclass
class Question:
    round: int
    category: str
    value: int
    question: str
    answer: str
    used: bool = False

@dataclass
class BuzzEntry:
    player_id: str
    player_name: str
    team_id: str
    team_name: str
    timestamp: float

@dataclass
class GameState:
    phase: GamePhase = GamePhase.LOBBY
    question_state: QuestionState = QuestionState.BOARD_ACTIVE
    teams: Dict[str, Team] = field(default_factory=dict)
    players: Dict[str, Player] = field(default_factory=dict)
    questions: List[Question] = field(default_factory=list)
    current_question: Optional[Question] = None
    buzz_queue: List[BuzzEntry] = field(default_factory=list)
    teams_attempted: List[str] = field(default_factory=list)  # Teams that attempted current question
    trebek_session_id: Optional[str] = None
    buzz_timer_active: bool = False
