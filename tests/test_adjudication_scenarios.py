"""
Comprehensive tests for adjudication and answer scoring functionality.
"""
import pytest
from app.game_logic import GameManager
from app.models import BuzzEntry, Question, QuestionState


class TestAdjudicateCorrectAnswer:
    """Tests for correct answer adjudication."""

    def test_adjudicate_correct_single_team(self, simple_game):
        """Test adjudicating correct answer with single buzzer."""
        gm, t1, t2, p1, p2, q = simple_game

        # Player 1 from team 1 buzzes
        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=p1.team_id, team_name='Alpha', timestamp=0)
        ]

        next_player, score_change = gm.adjudicate_answer(correct=True)

        assert next_player is None
        assert score_change == 100
        assert gm.state.current_question is None
        assert gm.state.buzz_queue == []
        assert gm.state.question_state == QuestionState.BOARD_ACTIVE
        assert gm.state.teams_attempted == []
        assert gm.state.teams[t1.id].score == 100

    def test_adjudicate_correct_updates_team_score(self, simple_game):
        """Test that correct answer updates team score correctly."""
        gm, t1, t2, p1, p2, q = simple_game

        # Set initial score
        gm.state.teams[t1.id].score = 50

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=p1.team_id, team_name='Alpha', timestamp=0)
        ]

        next_player, score_change = gm.adjudicate_answer(correct=True)

        assert gm.state.teams[t1.id].score == 150  # 50 + 100

    def test_adjudicate_correct_clears_state(self, simple_game):
        """Test that correct answer clears question-related state."""
        gm, t1, t2, p1, p2, q = simple_game

        gm.state.teams_attempted = [t1.id]  # Add some state to clear

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=p1.team_id, team_name='Alpha', timestamp=0)
        ]

        gm.adjudicate_answer(correct=True)

        assert gm.state.current_question is None
        assert gm.state.buzz_queue == []
        assert gm.state.teams_attempted == []
        assert gm.state.question_state == QuestionState.BOARD_ACTIVE

    def test_adjudicate_correct_returns_correct_score_change(self, simple_game):
        """Test that score change is question value for correct."""
        gm, t1, t2, p1, p2, q = simple_game

        # Create question with different value
        q.value = 500
        gm.state.current_question = q

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=p1.team_id, team_name='Alpha', timestamp=0)
        ]

        next_player, score_change = gm.adjudicate_answer(correct=True)

        assert score_change == 500


class TestAdjudicateWrongAnswerSingleBuzzer:
    """Tests for wrong answer adjudication with single buzzer."""

    def test_adjudicate_wrong_no_queue_remaining_teams(self, simple_game):
        """Test wrong answer with no queued buzzers but remaining teams."""
        gm, t1, t2, p1, p2, q = simple_game

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=p1.team_id, team_name='Alpha', timestamp=0)
        ]

        next_player, score_change = gm.adjudicate_answer(correct=False)

        # Should reopen buzzing for remaining team (t2)
        assert next_player is None
        assert score_change == -100
        assert gm.state.current_question is not None  # Question still active
        assert gm.state.question_state == QuestionState.BUZZING_OPEN
        assert t1.id in gm.state.teams_attempted
        assert gm.state.teams[t1.id].score == -100

    def test_adjudicate_wrong_deducts_score(self, simple_game):
        """Test that wrong answer deducts score."""
        gm, t1, t2, p1, p2, q = simple_game

        gm.state.teams[t1.id].score = 100

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=p1.team_id, team_name='Alpha', timestamp=0)
        ]

        gm.adjudicate_answer(correct=False)

        assert gm.state.teams[t1.id].score == 0  # 100 - 100

    def test_adjudicate_wrong_allows_negative_score(self, simple_game):
        """Test that score can go negative."""
        gm, t1, t2, p1, p2, q = simple_game

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=p1.team_id, team_name='Alpha', timestamp=0)
        ]

        gm.adjudicate_answer(correct=False)

        assert gm.state.teams[t1.id].score == -100


class TestAdjudicateWrongAnswerQueuedBuzzers:
    """Tests for wrong answer with queued buzzers."""

    def test_adjudicate_wrong_with_queued_buzzer(self, simple_game):
        """Test wrong answer with another player in queue."""
        gm, t1, t2, p1, p2, q = simple_game

        # Add both players to queue
        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=t1.id, team_name='Alpha', timestamp=0),
            BuzzEntry(player_id=p2.id, player_name=p2.name,
                     team_id=t2.id, team_name='Beta', timestamp=1)
        ]

        next_player, score_change = gm.adjudicate_answer(correct=False)

        assert next_player == p2.id
        assert score_change == -100
        assert gm.state.current_question is not None  # Question still active
        assert len(gm.state.buzz_queue) == 1
        assert gm.state.buzz_queue[0].player_id == p2.id
        assert t1.id in gm.state.teams_attempted

    def test_adjudicate_wrong_removes_from_queue(self, simple_game):
        """Test that wrong buzzer is removed from queue."""
        gm, t1, t2, p1, p2, q = simple_game

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=t1.id, team_name='Alpha', timestamp=0),
            BuzzEntry(player_id=p2.id, player_name=p2.name,
                     team_id=t2.id, team_name='Beta', timestamp=1)
        ]

        initial_queue_len = len(gm.state.buzz_queue)
        gm.adjudicate_answer(correct=False)

        assert len(gm.state.buzz_queue) == initial_queue_len - 1
        assert p1.id not in [e.player_id for e in gm.state.buzz_queue]


class TestAdjudicateAllTeamsAttempted:
    """Tests for adjudication when all teams have attempted."""

    def test_adjudicate_wrong_all_teams_attempted_ends_question(self, three_team_game):
        """Test that question ends when all teams attempted."""
        gm, teams, players = three_team_game

        # Set up question and simulate all teams attempting
        q = Question(round=1, category='Test', value=100,
                    question='Q?', answer='A')
        gm.state.current_question = q
        gm.state.question_state = QuestionState.BUZZING_OPEN

        # Add all teams to attempted
        gm.state.teams_attempted = [teams[0].id, teams[1].id]

        # Final buzzer from third team
        gm.state.buzz_queue = [
            BuzzEntry(player_id=players[2].id, player_name=players[2].name,
                     team_id=teams[2].id, team_name=teams[2].name, timestamp=0)
        ]

        next_player, score_change = gm.adjudicate_answer(correct=False)

        # Question should end
        assert gm.state.current_question is None
        assert gm.state.question_state == QuestionState.BOARD_ACTIVE
        assert gm.state.teams_attempted == []
        assert next_player is None


class TestAdjudicateEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_adjudicate_no_current_question(self, game_manager):
        """Test adjudication when no current question."""
        next_player, score_change = game_manager.adjudicate_answer(correct=True)

        assert next_player is None
        assert score_change == 0

    def test_adjudicate_empty_buzz_queue(self, game_manager):
        """Test adjudication with empty buzz queue."""
        q = Question(round=1, category='Test', value=100,
                    question='Q?', answer='A')
        game_manager.state.current_question = q
        game_manager.state.buzz_queue = []

        next_player, score_change = game_manager.adjudicate_answer(correct=True)

        assert next_player is None
        assert score_change == 0

    def test_adjudicate_no_question_no_queue(self, game_manager):
        """Test adjudication with both no question and no queue."""
        next_player, score_change = game_manager.adjudicate_answer(correct=True)

        assert next_player is None
        assert score_change == 0


class TestAdjudicateMultipleRounds:
    """Tests for adjudication with different question values (rounds)."""

    @pytest.mark.parametrize("value,expected_score", [
        (100, 100),
        (200, 200),
        (500, 500),
        (1000, 1000),
    ])
    def test_adjudicate_correct_different_values(self, simple_game, value, expected_score):
        """Test correct adjudication with different question values."""
        gm, t1, t2, p1, p2, q = simple_game

        q.value = value
        gm.state.current_question = q

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=t1.id, team_name='Alpha', timestamp=0)
        ]

        next_player, score_change = gm.adjudicate_answer(correct=True)

        assert score_change == expected_score
        assert gm.state.teams[t1.id].score == expected_score

    @pytest.mark.parametrize("value", [100, 200, 500, 1000])
    def test_adjudicate_wrong_different_values(self, simple_game, value):
        """Test wrong adjudication with different question values."""
        gm, t1, t2, p1, p2, q = simple_game

        q.value = value
        gm.state.current_question = q

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=t1.id, team_name='Alpha', timestamp=0)
        ]

        next_player, score_change = gm.adjudicate_answer(correct=False)

        assert score_change == -value
        assert gm.state.teams[t1.id].score == -value


class TestAdjudicateTeamsAttemptedTracking:
    """Tests for tracking which teams have attempted."""

    def test_teams_attempted_populated_on_wrong(self, simple_game):
        """Test that teams_attempted is updated on wrong answer."""
        gm, t1, t2, p1, p2, q = simple_game

        assert gm.state.teams_attempted == []

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=t1.id, team_name='Alpha', timestamp=0)
        ]

        gm.adjudicate_answer(correct=False)

        assert t1.id in gm.state.teams_attempted

    def test_teams_attempted_cleared_on_correct(self, simple_game):
        """Test that teams_attempted is cleared on correct answer."""
        gm, t1, t2, p1, p2, q = simple_game

        gm.state.teams_attempted = [t2.id]

        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=t1.id, team_name='Alpha', timestamp=0)
        ]

        gm.adjudicate_answer(correct=True)

        assert gm.state.teams_attempted == []

    def test_teams_attempted_not_duplicated(self, simple_game):
        """Test that same team not added twice to attempted."""
        gm, t1, t2, p1, p2, q = simple_game

        gm.state.teams_attempted = [t1.id]
        gm.state.buzz_queue = [
            BuzzEntry(player_id=p1.id, player_name=p1.name,
                     team_id=t1.id, team_name='Alpha', timestamp=0)
        ]

        gm.adjudicate_answer(correct=False)

        # Count occurrences
        count = gm.state.teams_attempted.count(t1.id)
        assert count == 1

