"""
Shared fixtures and utilities for all tests.
"""
import os
import csv
import tempfile
import pytest

from app.game_logic import GameManager
from app.models import Question, QuestionState


@pytest.fixture
def game_manager():
    """Fresh GameManager instance for each test."""
    return GameManager()


@pytest.fixture
def simple_game():
    """Pre-populated game with 2 teams, 2 players, and 1 question.

    Returns:
        tuple: (game_manager, team1, team2, player1, player2, question)
    """
    gm = GameManager()

    # Create teams
    t1 = gm.create_team('Alpha')
    t2 = gm.create_team('Beta')

    # Add players
    p1 = gm.add_player('Alice', t1.id, 's1')
    p2 = gm.add_player('Bob', t2.id, 's2')

    # Create and set question
    q = Question(round=1, category='Geography', value=100,
                 question='What is the capital of France?', answer='Paris')
    gm.state.questions = [q]
    gm.state.current_question = q
    gm.state.question_state = QuestionState.BUZZING_OPEN
    gm.state.buzz_timer_active = False

    return gm, t1, t2, p1, p2, q


@pytest.fixture
def three_team_game():
    """Game with 3 teams and players for testing multiple team scenarios."""
    gm = GameManager()

    teams = [
        gm.create_team('Alpha'),
        gm.create_team('Beta'),
        gm.create_team('Gamma')
    ]

    players = [
        gm.add_player('Alice', teams[0].id, 's1'),
        gm.add_player('Bob', teams[1].id, 's2'),
        gm.add_player('Charlie', teams[2].id, 's3')
    ]

    return gm, teams, players


@pytest.fixture
def sample_questions_csv(tmp_path):
    """Create a temporary CSV file with sample questions.

    Returns:
        str: Path to the temporary CSV file
    """
    csv_file = tmp_path / "questions.csv"

    questions = [
        ['Round', 'Category', 'Value', 'Question', 'Answer'],
        ['1', 'Geography', '100', 'Capital of France?', 'Paris'],
        ['1', 'Geography', '200', 'Capital of Germany?', 'Berlin'],
        ['1', 'Science', '100', 'What is H2O?', 'Water'],
        ['1', 'Science', '200', 'What is Fe?', 'Iron'],
        ['2', 'History', '200', 'Year of Moon Landing?', '1969'],
        ['2', 'History', '400', 'Who was first President?', 'George Washington'],
    ]

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(questions)

    return str(csv_file)


@pytest.fixture
def mock_questions_file(monkeypatch, sample_questions_csv):
    """Mock the Config.QUESTIONS_FILE path.

    Args:
        monkeypatch: pytest's monkeypatch fixture
        sample_questions_csv: Path to sample CSV
    """
    from config import Config
    monkeypatch.setattr(Config, 'QUESTIONS_FILE', sample_questions_csv)
    return sample_questions_csv


@pytest.fixture
def full_round_questions():
    """Create a complete round of questions for board state testing."""
    questions = [
        Question(round=1, category='Geography', value=100,
                question='Q1', answer='A1', used=False),
        Question(round=1, category='Geography', value=200,
                question='Q2', answer='A2', used=False),
        Question(round=1, category='Science', value=100,
                question='Q3', answer='A3', used=False),
        Question(round=1, category='Science', value=200,
                question='Q4', answer='A4', used=False),
    ]
    return questions

