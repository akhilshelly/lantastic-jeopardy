"""
Tests for question loading from CSV and board state functionality.
"""
import os
import csv
import pytest
from app.game_logic import GameManager
from app.models import Question


class TestQuestionLoading:
    """Tests for loading questions from CSV file."""

    def test_load_questions_success(self, game_manager, mock_questions_file):
        """Test successfully loading questions from CSV."""
        result = game_manager.load_questions()

        assert result is True
        assert len(game_manager.state.questions) > 0

    def test_load_questions_count(self, game_manager, mock_questions_file):
        """Test that correct number of questions are loaded."""
        game_manager.load_questions()

        # Sample file has 6 data rows (excluding header)
        assert len(game_manager.state.questions) == 6

    def test_load_questions_structure(self, game_manager, mock_questions_file):
        """Test that questions have correct structure."""
        game_manager.load_questions()

        question = game_manager.state.questions[0]

        assert hasattr(question, 'round')
        assert hasattr(question, 'category')
        assert hasattr(question, 'value')
        assert hasattr(question, 'question')
        assert hasattr(question, 'answer')
        assert hasattr(question, 'used')

    def test_load_questions_values_correct(self, game_manager, mock_questions_file):
        """Test that question values are parsed correctly."""
        game_manager.load_questions()

        # First question from sample file
        q1 = game_manager.state.questions[0]
        assert q1.round == 1
        assert q1.category == 'Geography'
        assert q1.value == 100
        assert q1.question == 'Capital of France?'
        assert q1.answer == 'Paris'

    def test_load_questions_used_defaults_false(self, game_manager, mock_questions_file):
        """Test that questions start with used=False."""
        game_manager.load_questions()

        for question in game_manager.state.questions:
            assert question.used is False

    def test_load_questions_clears_previous_questions(self, game_manager, mock_questions_file):
        """Test that loading questions clears previous questions."""
        # Add a dummy question
        q1 = Question(round=1, category='Dummy', value=1,
                     question='Dummy?', answer='Dummy')
        game_manager.state.questions = [q1]

        assert len(game_manager.state.questions) == 1

        game_manager.load_questions()

        # Should have loaded questions from file, not have dummy
        assert len(game_manager.state.questions) > 0
        assert all(q.category != 'Dummy' for q in game_manager.state.questions)


class TestQuestionLoadingErrors:
    """Tests for error handling during question loading."""

    def test_load_questions_file_not_found(self, game_manager):
        """Test loading when file doesn't exist."""
        from config import Config
        import unittest.mock as mock

        # Mock the path to a file that definitely doesn't exist
        with mock.patch.object(Config, 'QUESTIONS_FILE', '/nonexistent/path/questions.csv'):
            result = game_manager.load_questions()

        assert result is False
        assert len(game_manager.state.questions) == 0

    def test_load_questions_invalid_csv_format(self, game_manager, tmp_path):
        """Test loading malformed CSV."""
        # Create an invalid CSV file
        csv_file = tmp_path / "invalid.csv"
        with open(csv_file, 'w') as f:
            f.write("This is not valid CSV\n")
            f.write("It has incomplete,data")

        from config import Config
        import unittest.mock as mock
        with mock.patch.object(Config, 'QUESTIONS_FILE', str(csv_file)):
            result = game_manager.load_questions()

        # Should fail gracefully
        assert result is False

    def test_load_questions_empty_file(self, game_manager, tmp_path):
        """Test loading empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        from config import Config
        import unittest.mock as mock
        with mock.patch.object(Config, 'QUESTIONS_FILE', str(csv_file)):
            result = game_manager.load_questions()

        # Empty file with no questions should return False
        assert result is False

    def test_load_questions_header_only(self, game_manager, tmp_path):
        """Test loading CSV with header but no data."""
        csv_file = tmp_path / "header_only.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Round', 'Category', 'Value', 'Question', 'Answer'])

        from config import Config
        import unittest.mock as mock
        with mock.patch.object(Config, 'QUESTIONS_FILE', str(csv_file)):
            result = game_manager.load_questions()

        # No questions = False
        assert result is False


class TestBoardState:
    """Tests for getting board state."""

    def test_get_board_state_basic(self, game_manager, full_round_questions):
        """Test getting board state for a round."""
        game_manager.state.questions = full_round_questions

        board = game_manager.get_board_state(1)

        assert board is not None
        assert isinstance(board, dict)
        assert 'Geography' in board
        assert 'Science' in board

    def test_get_board_state_organized_by_category(self, game_manager, full_round_questions):
        """Test that board is organized by category."""
        game_manager.state.questions = full_round_questions

        board = game_manager.get_board_state(1)

        assert len(board['Geography']) == 2
        assert len(board['Science']) == 2

    def test_get_board_state_values_sorted(self, game_manager, full_round_questions):
        """Test that values are sorted within each category."""
        game_manager.state.questions = full_round_questions

        board = game_manager.get_board_state(1)

        geo_values = [q['value'] for q in board['Geography']]
        sci_values = [q['value'] for q in board['Science']]

        assert geo_values == sorted(geo_values)
        assert sci_values == sorted(sci_values)

    def test_get_board_state_includes_question_data(self, game_manager, full_round_questions):
        """Test that board state includes question text and answer."""
        game_manager.state.questions = full_round_questions

        board = game_manager.get_board_state(1)

        question = board['Geography'][0]
        assert 'value' in question
        assert 'used' in question
        assert 'question' in question
        assert 'answer' in question

    def test_get_board_state_marks_used_questions(self, game_manager, full_round_questions):
        """Test that used questions are marked in board state."""
        full_round_questions[0].used = True
        game_manager.state.questions = full_round_questions

        board = game_manager.get_board_state(1)

        assert board['Geography'][0]['used'] is True
        assert board['Geography'][1]['used'] is False

    def test_get_board_state_single_round(self, game_manager, full_round_questions):
        """Test that board state filters by round."""
        # Add round 2 questions
        full_round_questions.append(
            Question(round=2, category='Geography', value=200,
                    question='Q5', answer='A5', used=False)
        )
        game_manager.state.questions = full_round_questions

        board1 = game_manager.get_board_state(1)
        board2 = game_manager.get_board_state(2)

        # Round 1 should have 4 questions (2 categories, 2 values each)
        total_r1 = sum(len(q) for q in board1.values())
        assert total_r1 == 4

        # Round 2 should have 1 question
        total_r2 = sum(len(q) for q in board2.values())
        assert total_r2 == 1


class TestBoardStateEmpty:
    """Tests for board state with no/empty questions."""

    def test_get_board_state_no_questions(self, game_manager):
        """Test board state when no questions loaded."""
        board = game_manager.get_board_state(1)

        assert board == {}

    def test_get_board_state_round_with_no_questions(self, game_manager, full_round_questions):
        """Test board state for round that has no questions."""
        game_manager.state.questions = full_round_questions  # All round 1

        board = game_manager.get_board_state(2)  # Request round 2

        assert board == {}


class TestQuestionCategories:
    """Tests for question categorization."""

    def test_get_board_state_multiple_categories(self, game_manager):
        """Test board with multiple categories."""
        questions = [
            Question(round=1, category='Geography', value=100, question='Q1', answer='A1'),
            Question(round=1, category='Science', value=100, question='Q2', answer='A2'),
            Question(round=1, category='History', value=100, question='Q3', answer='A3'),
            Question(round=1, category='Literature', value=100, question='Q4', answer='A4'),
        ]
        game_manager.state.questions = questions

        board = game_manager.get_board_state(1)

        assert len(board) == 4
        assert 'Geography' in board
        assert 'Science' in board
        assert 'History' in board
        assert 'Literature' in board

    def test_get_board_state_same_category_different_values(self, game_manager):
        """Test multiple values for same category."""
        questions = [
            Question(round=1, category='Geography', value=100, question='Q1', answer='A1'),
            Question(round=1, category='Geography', value=200, question='Q2', answer='A2'),
            Question(round=1, category='Geography', value=300, question='Q3', answer='A3'),
        ]
        game_manager.state.questions = questions

        board = game_manager.get_board_state(1)

        assert len(board['Geography']) == 3
        assert board['Geography'][0]['value'] == 100
        assert board['Geography'][1]['value'] == 200
        assert board['Geography'][2]['value'] == 300

